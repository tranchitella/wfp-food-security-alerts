import csv
import logging
import requests
import sqlite3

from contextlib import closing
from typing import Iterator, Optional


class PopulationService(object):

    _db: sqlite3.Connection
    _logger: logging.Logger
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._db = None
        self._logger = logger

    def connect(self, db_population: str) -> sqlite3.Connection:
        db = sqlite3.connect(db_population)
        self._db = db
        return db

    def close(self) -> sqlite3.Connection:
        self._db.close()
        self._db = None

    def log_debug(self, *args, **kw):
        if self._logger is not None:
            self._logger.debug(*args, **kw)
            
    def log_warning(self, *args, **kw):
        if self._logger is not None:
            self._logger.warning(*args, **kw)
            
    def log_error(self, *args, **kw):
        if self._logger is not None:
            self._logger.error(*args, **kw)
            
    def download(
        self, url: str, 
    ) -> int:
        iterator = self.get_rows_from_url(url)
        return self.write_rows_to_sqlite(iterator)

    def get_rows_from_url(
        self, url: str, logger: Optional[logging.Logger] = None
    ) -> Iterator[dict]:
        self.log_debug("Downloading population data from %s", url)
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
                        self.log_warning(
                            "Skip line %d, wrong number of columns: %s", n + 1, row
                        )
                        continue
                    try:
                        values = map(int, row)
                    except (ValueError, TypeError):
                        self.log_warning(
                            "Ignore line %d, unable to convert values to int: %s",
                            n + 1,
                            row,
                        )
                    data = dict(zip(header, values))
                    yield data
        except requests.exceptions.HTTPError as e:
            self.log_error('Unable to download the data: %s', e)

    def write_rows_to_sqlite(
        self,
        iterator: Iterator[dict],
        logger: Optional[logging.Logger] = None,
    ) -> int:
        self._db.execute("DROP TABLE IF EXISTS population;")
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS population (region_id INTEGER PRIMARY KEY, population INTEGER);"
        )
        n = -1
        for n, row in enumerate(iterator):
            self._db.execute(
                "INSERT INTO population (region_id, population) VALUES (?, ?);",
                [row['region_id'], row['population']],
            )
        self.log_debug("Inserted %d records into the population database", n + 1)
        self._db.commit()
        return n + 1


    def get_population_by_region_id(
        self, region_id: int
    ) -> Optional[int]:
        c = self._db.execute(
            "SELECT population FROM population WHERE region_id = ?;", [region_id]
        )
        row = c.fetchone()
        return row[0] if row is not None else None
