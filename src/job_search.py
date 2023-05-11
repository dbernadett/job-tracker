import argparse
import csv
import logging
import os
import sqlite3
import sys
from datetime import date
from urllib.parse import urlparse
from urllib.parse import urlunparse

from download_cruise import CruiseDownloader
from download_zoox import ZooxDownloader

TABLE_NAME = "job_opportunities"

parser = argparse.ArgumentParser(prog="job_search", description="Job Search CLI")
parser.add_argument("-c", "--dir", help="Directory to work from", default=".")
subparsers = parser.add_subparsers(dest="command")

# init command
init_parser = subparsers.add_parser("init", description="Initialize the database")

# add command
add_parser = subparsers.add_parser("add", description="Add a new job opportunity")
add_parser.add_argument(
    "--redownload", help="Redownload the HTML", action="store_true", default=False
)
add_parser.add_argument(
    "--reparse", help="Reparse the HTML", action="store_true", default=False
)
add_parser.add_argument("url")

# open command
open_parser = subparsers.add_parser("open")
open_parser.add_argument("id")

# list command
list_parser = subparsers.add_parser("list")

# query command
query_parser = subparsers.add_parser("query")
query_parser.add_argument("sql_query")

# stats command
stats_parser = subparsers.add_parser("stats")

args = parser.parse_args()

# Create a logger
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.INFO)
# Create a console handler
handler = logging.StreamHandler()
# Set the logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)


def get_db_path(dir):
    return os.path.join(dir, "records.db")


def get_archive_path(dir):
    return os.path.join(dir, "html_archive")


def get_db_archive_or_fail(workspace):
    init_file = os.path.join(workspace, ".job_search")
    if not os.path.exists(init_file):
        logger.error(
            f'Could not find job_search file: "{init_file}" This directory is not a job_search repo.'
        )
        exit(1)
    db_path, archive_path = get_db_path(workspace), get_archive_path(workspace)
    # Create a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    text_fields = ["title", "company", "date_posted", "date_applied", "url"]
    create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id INTEGER, {', '.join([f'{field} TEXT' for field in text_fields])}, PRIMARY KEY (id AUTOINCREMENT), UNIQUE (url))"
    cursor.execute(create_table_query)
    return cursor, archive_path


def is_url_present(cursor, url):
    select_query = "SELECT COUNT(*) FROM job_opportunities WHERE url = ?"
    cursor.execute(select_query, (url,))
    count = cursor.fetchone()[0]
    return count > 0


def init(**kwargs):
    print(kwargs)
    workspace = kwargs["dir"]
    print(workspace)
    init_file = os.path.join(workspace, ".job_search")
    if os.path.exists(init_file):
        logger.error(
            f'Could not initialize job_search repo. File already exists: "{init_file}"'
        )
        exit(1)
    else:
        with open(init_file, "w") as f:
            f.write("version=1.0")
        logger.info(f"Initialized job_search repo in {workspace}")


def add(url, redownload, reparse, **kwargs):
    supported_domains = {"zoox.com": ZooxDownloader, "getcruise.com": CruiseDownloader}
    cursor, archive = get_db_archive_or_fail(kwargs["dir"])
    url = urlparse(url)
    if url.hostname not in supported_domains:
        logger.warning(
            f"Could not download {url.hostname} because it is not supported yet. Please add support for it in download.py"
        )
        exit(1)

    if is_url_present(cursor, urlunparse(url)) and not redownload and not reparse:
        logger.warning(
            f"DUPLICATE URL {urlunparse(url)} already present in the database. Skipping."
        )
        exit(1)

    if not is_url_present(cursor, urlunparse(url)):
        # Insert a new record into the table
        insert_query = f"INSERT INTO {TABLE_NAME} (id, title, company, date_posted, date_applied, url) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(
            insert_query, (None, "", "", str(date.today()), "", urlunparse(url))
        )
        logger.info(f"Downloading new record with URL {urlunparse(url)}")
    else:
        select_query = "SELECT id FROM job_opportunities WHERE url = ?"
        cursor.execute(select_query, (urlunparse(url),))
        record_id = cursor.fetchone()[0]
        logger.info(f"Found record {record_id} with same URL {urlunparse(url)}")

    # Get the ID of the new record
    record_id = cursor.lastrowid

    # Download the URL and save it as an HTML file
    parsed_fields = None

    if url.hostname in supported_domains:
        download_function = supported_domains[url.hostname]
        logger.info(
            f"Calling download_and_parse {urlunparse(url)} with parser {download_function.__name__}"
        )
        downloader = download_function(archive)
        parsed_fields = downloader.download_and_parse(
            urlunparse(url), record_id, archive, redownload
        )
    else:
        logger.error(
            f"Could not download {url.hostname} because it is not supported yet. Please add support for it in download.py"
        )
        exit(1)

    # Update the record with the title
    title = parsed_fields["title"]
    company = parsed_fields["company"]
    logger.info(f"Updating record {record_id} with title {title}")

    update_query = f"UPDATE {TABLE_NAME} SET title = ?, company = ? WHERE id = ?"
    cursor.execute(update_query, (title, company, record_id))
    print(f"add command called with url: {url}")


def open_cmd(id, **kwargs):
    cursor, archive = get_db_archive_or_fail(kwargs["dir"])
    # Check to make sure id exists in both the database and the archive
    cursor.execute(f"SELECT url FROM {TABLE_NAME} WHERE id = {id}")
    url = os.path.join(archive, f"{id}.html")
    if not os.path.exists(url) or not cursor.fetchone():
        logger.error(f"Could not find job opportunity with id: {id}")
        exit(1)
    os.system(f"open {url}")
    print(f"open command called with id: {id}")


def list(**kwargs):
    cursor, _ = get_db_archive_or_fail(kwargs["dir"])
    # Print all records in the table
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    writer = csv.writer(sys.stdout, delimiter=",")
    # Write the header row
    writer.writerow([description[0] for description in cursor.description])
    # Write the data rows
    for row in rows:
        writer.writerow(row)
        # pretty print results as a csv


def stats(**kwargs):
    cursor, _ = get_db_archive_or_fail(kwargs["dir"])
    # Print the number of records in the table
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    print(f"Number of saved postings: {cursor.fetchone()[0]}")
    # Count number of openings grouped by company
    cursor.execute(f"SELECT company, COUNT(*) FROM {TABLE_NAME} GROUP BY company")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}")


commands = {
    None: lambda **kwargs: parser.print_help(),
    "init": init,
    "add": add,
    "open": open_cmd,
    "list": list,
    "stats": stats,
}

commands[args.command](**vars(args))
