import os

from wfp_food_security_alerts import population


def test_write_rows_to_sqlite_and_get_population_by_region(tmpdir):
    database = os.path.join(tmpdir, 'population.sqlite3')
    iterator = [
        {"region_id": 1, "population": 1000},
        {"region_id": 2, "population": 2000},
    ]
    db = population.get_sqlite3_connection(database)
    #
    try:
        rows = population.write_rows_to_sqlite(db, iterator)
        assert 2 == rows
        value = population.get_population_by_region_id(db, 1)
        assert 1000 == value
        value = population.get_population_by_region_id(db, 2)
        assert 2000 == value
        value = population.get_population_by_region_id(db, 999)
        assert value is None
    finally:
        db.close()
