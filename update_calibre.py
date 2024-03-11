import calibre.library
from calibre.ebooks.metadata import title_sort, authors_to_sort_string
import os
import re
import json
import datetime
from config import config

calibre_db = calibre.library.db(config.CALIBRE_DB_PATH).new_api


def get_calibre_books():
    """Get the list of books and authors from my Calibre eBook library."""
    # First open the Calibre library and get a list of the book IDs

    book_ids = calibre_db.all_book_ids()
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        print(book)
        break
    print("Got {} book IDs from Calibre library".format(len(book_ids)))


def get_all_books_by_series(series_name: str):
    """Get all books in a series.

    Args:
        series_name: The name of the series to search for.
    """
    book_ids = calibre_db.all_book_ids()
    books = []
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        if book.series == series_name:
            books.append(book)
    return books


def get_all_books_without_series():
    """Get all books in the Calibre library without a series."""
    book_ids = calibre_db.all_book_ids()
    books = []
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        if not book.series:
            books.append(book)
    return books


def get_all_series():
    """Get all series in the Calibre library."""
    book_ids = calibre_db.all_book_ids()
    series = set()
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        series.add(book.series)
    return series


def get_serie_index_from_title(title: str):
    """Get the index of the series from the title.
    It has various formats like:
        #1 - The Black Company
        #02
        Dragonlance Vol.3
        v1
    etc...
    """
    match = re.search(r"#?(\d+)", title)
    if match:
        return int(match.group(1))
    return None


def load_results():
    f_path = os.path.join(os.path.dirname(__file__), "output/results.json")
    f = open(f_path, "r")
    return json.load(f)


def build_black_list_titles(issue):
    return [
        "vol.{}".format(issue["issue_number"]),
        "volume{}".format(issue["issue_number"]),
        "vol{}".format(issue["issue_number"]),
        "#{}".format(issue["issue_number"]),
    ]


def calibre_update_metadata(book, issue, issue_nb_padding=2):
    """Update the metadata of the book in the Calibre library."""
    mi = calibre_db.get_metadata(book.id)
    black_list_titles = build_black_list_titles(issue)
    issue["name"] = issue["name"] or ""
    if issue["name"].lower().replace(" ", "") in black_list_titles:
        mi.title = "{} - Vol. {}".format(
            issue["volume"], str(issue["issue_number"]).zfill(issue_nb_padding)
        )
    else:
        mi.title = "{} - Vol. {}: {}".format(
            issue["volume"],
            str(issue["issue_number"]).zfill(issue_nb_padding),
            issue["name"],
        )
    mi.series = issue["volume"]
    mi.series_index = float(issue["issue_number"])
    mi.comments = issue["description"]
    mi.authors = issue["person_credits"]
    mi.pubdate = datetime.datetime.strptime(issue["cover_date"], "%Y-%m-%d")
    mi.publisher = issue["publisher"]

    # Sort title
    mi.title_sort = title_sort(mi.title)
    # Sort author(s)
    mi.author_sort = authors_to_sort_string(mi.authors)

    calibre_db.set_metadata(book.id, mi)

    print("Updated metadata for book: {}".format(book.title))


if __name__ == "__main__":
    results = load_results()
    if len(results) == 0:
        print("No results found")
        exit(1)
    search_term = results[0]["volume"]
    books = get_all_books_by_series(search_term)
    if len(books) == 0:
        print("No books found for series: {}".format(search_term))
        books = get_all_books_without_series()
        print("Found {} books without series".format(len(books)))
        if len(books) == 0:
            print("No books found without series")
            exit(1)
    else:
        print("Found {} books for series: {}".format(len(books), search_term))
    serie_index_results = {}
    for result in results:
        serie_index_results[int(result["issue_number"])] = result

    issue_nb_padding = len(str(len(books)))
    for book in books:
        serie_index = get_serie_index_from_title(book.title)
        if serie_index is None and book.series_index:
            serie_index = int(book.series_index)
        # Sometimes the volume number is in the author field
        if serie_index is None and book.authors:
            serie_index = get_serie_index_from_title(book.authors[0])

        if serie_index is not None:
            print(book.title + " - " + str(serie_index))
            result = serie_index_results.get(serie_index)
            if result:
                print("Updating metadata for book: {}".format(book.title))
                calibre_update_metadata(book, result, issue_nb_padding)

    print("Done")
