Calibre Comic Vine Scraper
==========================

Scraps metadata for manga from the ComicVine database and updates the metadata in the calibre library.
Two scripts need to be run in sequence to update the metadata. One scraps the metadata and the other updates the calibre library.

I did not do them in one script because I wanted to be able to review the metadata before updating the calibre library.
Also I was not sure how to install extra python packages in the calibre environment.

Install
-------

```pip install -r requirements.txt```

And you need to have calibre installed and the calibre-debug command in your path.

Configure
---------

Rename `config.json.sample` to `config.json` and update the values accordingly.

- COMIC_VINE_API_KEY: You need to register for an API key at https://comicvine.gamespot.com/api/
- CALIBRE_LIBRARY_PATH: The path to the calibre library. This is the path to the folder that contains the metadata.db file.
- UNIQUE_AGENT_ID: This is the unique agent ID used to fetch data on ComicVine as per the API documentation. It says to use something unique and meaningful. E.g: "ajite super manga fet

Scrap
-----

```python comic_vine.py "Name of the Manga"```

You will be prompted to select the correct series from the list of series returned by the search.
This will create a file called "output/results.json" with the metadata for the manga.

You can also use the --start and --end options to scrap a range of volumes.

```python comic_vine.py "Name of the Manga" --start 1 --end 10```

This will scrap the metadata for volumes 1 to 10.

When scraping only one volume you can either use the --start or --end option.

E.g:

```python comic_vine.py "Name of the Manga" --start 1```

The program will swap the --start for --end when the start is greater than the end.

```python comic_vine.py "Name of the Manga" --start 1```

```python comic_vine.py "Name of the Manga" --end 1```

.. warning::
    You are limited to 200 requests per resource per hour. So if you have a lot of volumes to scrap you might want to do it in batches.
    This script also takes 1 sec to sleep between requests to avoid hitting the rate limit.

Run
---

Make sure that the series is in the calibre under the name of "volume" from results.json.
You can select all the volume from a series in calibre and mass update the "series" metadata to the name of the series.
E.g: "One Piece" for all the volumes of One Piece. The series_index does not matter. It will be updated by the script.

.. note::
    You need to have calibre installed and the calibre-debug command in your path.

On windows I use the following batch file to run the script:

```./run.bat```

.. warning::
    You might need to update the path to the calibre-debug command in the batch file.

At the moment I only fetch the following metadata:
- Name
- Volume
- Issue Number
- Cover Date
- Description
- Person Credits
- Publisher

Regarding the Person Credits, I only fetch the writer and artist. I might add more in the future.

Disclaimer
----------

These scripts are provided as is and I take no responsibility for any damage they might cause to your calibre library. Use at your own risk.
I made these scripts quickly to update my own library and I am sharing them in case they are useful to someone else.

Feel free to fork and improve them.
