import csv
import logging
import requests
import sqlite3

from contextlib import closing
from typing import Iterator, Optional


def download(
    db_population: str, url: str, logger: Optional[logging.Logger] = None
) -> int:
    iterator = get_rows_from_url(url, logger=logger)
    db = get_sqlite3_connection(db_population)
    try:
        return write_rows_to_sqlite(db, iterator, logger=logger)
    finally:
        db.close()


def get_rows_from_url(
    url: str, logger: Optional[logging.Logger] = None
) -> Iterator[dict]:
    if logger is not None:
        logger.debug("Downloading population data from %s", url)
    try:
        with closing(requests.get(url, stream=True)) as r:
            r.raise_for_status()
            lines = r.iter_lines(decode_unicode=True)
            reader = csv.reader(lines, delimiter=',', quotechar='"')
            header = None
            for n, row in enumerate(reader):
                if header is None:
                    header = row
                    continue
                elif len(row) != len(header):
                    if logger is not None:
                        logger.warning(
                            "Skip line %d, wrong number of columns: %s", n + 1, row
                        )
                    continue
                try:
                    values = map(int, row)
                except (ValueError, TypeError):
                    if logger is not None:
                        logger.warning(
                            "Ignore line %d, unable to convert values to int: %s",
                            n + 1,
                            row,
                        )
                data = dict(zip(header, values))
                yield data
    except requests.exceptions.HTTPError as e:
        if logger is not None:
            logger.error('Unable to download the data: %s', e)


def get_sqlite3_connection(db_population: str) -> sqlite3.Connection:
    return sqlite3.connect(db_population)


def write_rows_to_sqlite(
    db: sqlite3.Connection,
    iterator: Iterator[dict],
    logger: Optional[logging.Logger] = None,
) -> int:
    db.execute("DROP TABLE IF EXISTS population;")
    db.execute(
        "CREATE TABLE IF NOT EXISTS population (region_id INTEGER PRIMARY KEY, population INTEGER);"
    )
    n = -1
    for n, row in enumerate(iterator):
        db.execute(
            "INSERT INTO population (region_id, population) VALUES (?, ?);",
            [row['region_id'], row['population']],
        )
    if logger is not None:
        logger.debug("Inserted %d records into the population database", n + 1)
    db.commit()
    return n + 1


def get_population_by_region_id(
    db: sqlite3.Connection, region_id: int
) -> Optional[int]:
    c = db.execute(
        "SELECT population FROM population WHERE region_id = ?;", [region_id]
    )
    row = c.fetchone()
    return row[0] if row is not None else None
