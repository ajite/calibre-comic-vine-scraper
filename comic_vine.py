import json
import time
import requests
import argparse
from config import config
import sys

COMIC_VINE_API_URL = "https://comicvine.gamespot.com/api"
UNIQUE_AGENT_ID = config.UNIQUE_AGENT_ID


class Volume:
    def __init__(
        self,
        name: str,
        start_year: int,
        publisher: str,
        count_of_issues: int = 0,
        api_detail_url: str = None,
    ):
        self.name = name
        self.start_year = start_year
        self.publisher = publisher
        self.count_of_issues = count_of_issues
        self.api_detail_url = api_detail_url

    def __repr__(self):
        return "Volume(name={}, start_year={}, publisher={}, nb_volumes={})".format(
            self.name, self.start_year, self.publisher, self.count_of_issues
        )

    def __str__(self):
        return "{} ({}), published by {} - {} volumes".format(
            self.name, self.start_year, self.publisher, self.count_of_issues
        )

    @classmethod
    def from_json(cls, json_data):
        return cls(
            name=json_data["name"],
            start_year=json_data["start_year"],
            publisher=json_data.get("publisher", {}).get("name", ""),
            count_of_issues=json_data["count_of_issues"],
            api_detail_url=json_data["api_detail_url"],
        )


class Issue:
    def __init__(
        self,
        name: str,
        issue_number: int,
        cover_date: str,
        description: str,
        person_credits: list,
        api_detail_url: str = None,
        volume: Volume = None,
    ):
        self.name = name
        self.issue_number = issue_number
        self.cover_date = cover_date
        self.description = description
        self.person_credits = self._keep_only_writer_and_artist(person_credits)
        self.api_detail_url = api_detail_url
        self.volume = volume

    def _keep_only_writer_and_artist(self, person_credits: list):
        """Keep only the writer and artist from the person credits."""
        return [
            person["name"]
            for person in person_credits
            if "writer" in person["role"].lower() or "artist" in person["role"].lower()
        ]

    def __repr__(self):
        return (
            "Issue(name={}, issue_number={}, cover_date={}, person_credits={})".format(
                self.name,
                self.issue_number,
                self.cover_date,
                " ,".join(self.person_credits),
            )
        )

    def __str__(self):
        return "{} ({}), published on {} - {}".format(
            self.name,
            self.issue_number,
            self.cover_date,
            " ,".join(self.person_credits),
        )

    @classmethod
    def from_json(cls, json_data, volume: Volume):
        return cls(
            name=json_data["name"],
            issue_number=json_data["issue_number"],
            cover_date=json_data["cover_date"],
            description=json_data["description"],
            person_credits=json_data["person_credits"],
            api_detail_url=json_data["api_detail_url"],
            volume=volume,
        )

    @property
    def output(self):
        return {
            "name": self.name,
            "volume": self.volume.name if self.volume else None,
            "issue_number": self.issue_number,
            "cover_date": self.cover_date,
            "description": self.description,
            "person_credits": self.person_credits,
            "publisher": self.volume.publisher if self.volume else "",
        }


def get_request(url: str, params=None):
    """Make a GET request to the Comic Vine API."""
    headers = {"User-Agent": UNIQUE_AGENT_ID}
    if params is None:
        params = {}
    # Add the API key to the parameters
    params.update({"api_key": config.COMIC_VINE_API_KEY, "format": "json"})
    response = requests.get(url, headers=headers, params=params)
    # Check for API limit
    if response.status_code == 420:
        print("API limit reached")
        sys.exit(1)
    f = open("output/comic_vine_response.json", "w")
    # Pretty print the JSON response with 4 spaces
    f.write(json.dumps(response.json(), indent=4))
    f.close()
    # Add a delay to avoid reaching the rate limit
    time.sleep(1)
    return response.json()


def get_comic_vine_volumes(volume_name: str):
    """Get volumes from the Comic Vine API matching the given name.

    Args:
        volume_name: The name of the volume to search for.
    """
    url = "{}/volumes/".format(COMIC_VINE_API_URL)
    params = {"filter": "name:{}".format(volume_name)}
    response = get_request(url, params)
    volumes = []
    for volume in response["results"]:
        try:
            volumes.append(Volume.from_json(volume))
        except Exception:
            continue
    return volumes


def print_download_progress(chunk_number, chunk_size, total_size):
    """Print the download progress."""
    percent = 100 * chunk_number * chunk_size / total_size
    print("Downloaded {}%".format(int(percent)))


if __name__ == "__main__":
    # Use argparse to get the search term
    parser = argparse.ArgumentParser("search for a volume on Comic Vine")
    parser.add_argument("search_term", help="The volume to search for. E.g: One Piece")
    # Additional arguments to parse a range of volumes only. E.g: Vol 1 to 10
    parser.add_argument("--start", type=int, help="The start of the range")
    parser.add_argument("--end", type=int, help="The end of the range")
    args = parser.parse_args()

    # If start is greater than end, swap the values
    if args.start and args.end and args.start > args.end:
        args.start, args.end = args.end, args.start
    # If start is provided but not end, set end to start
    if args.start and not args.end:
        args.end = args.start
    # If end is provided but not start, set start to end
    if args.end and not args.start:
        args.start = args.end

    volumes = get_comic_vine_volumes(args.search_term)
    # Select a volume from the list
    for i, volume in enumerate(volumes):
        print("{}: {}".format(i, volume))
    # Get the user's choice
    choice = int(input("Choose a volume: "))
    volume = get_request(volumes[choice].api_detail_url)
    issues = []
    max_issues = volume["results"]["count_of_issues"]
    if args.start and args.end:
        max_issues = args.end - args.start + 1

    # Get the issues from the volume
    i = 0
    for issue in volume["results"]["issues"]:
        issue_number = int(issue.get("issue_number", "0"))
        if (
            args.start
            and args.end
            and (issue_number < args.start or issue_number > args.end)
        ):
            continue
        print_download_progress(i, 1, max_issues)
        i += 1
        issues.append(
            Issue.from_json(
                get_request(issue["api_detail_url"])["results"], volume=volumes[choice]
            )
        )

    # Save the issues to a JSON file
    f = open("output/results.json", "w")
    f.write(json.dumps([issue.output for issue in issues], indent=4))
    f.close()
