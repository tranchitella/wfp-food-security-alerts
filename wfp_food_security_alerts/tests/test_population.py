import os

from wfp_food_security_alerts.population import PopulationService


def test_write_rows_to_sqlite_and_get_population_by_region(tmpdir):
    database = os.path.join(tmpdir, 'population.sqlite3')
    iterator = [
        {"region_id": 1, "population": 1000},
        {"region_id": 2, "population": 2000},
    ]
    db = PopulationService()
    db.connect(database)
    #
    try:
        rows = db.write_rows_to_sqlite(iterator)
        assert 2 == rows
        value = db.get_population_by_region_id(1)
        assert 1000 == value
        value = db.get_population_by_region_id(2)
        assert 2000 == value
        value = db.get_population_by_region_id(999)
        assert value is None
    finally:
        db.close()


def test_get_rows_from_url():
    db = PopulationService()
    iterator = db.get_rows_from_url(
        "https://api.hungermapdata.org/swe-notifications/population.csv"
    )
    item = next(iterator)
    assert item is not None
    assert item['region_id'] is not None
    assert item['population'] is not None
