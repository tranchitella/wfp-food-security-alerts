from wfp_food_security_alerts.api import APIService


API_FOOD_SECURITY = "https://api.hungermapdata.org/swe-notifications/foodsecurity"
API_COUNTRY_REGIONS = (
    "https://api.hungermapdata.org/swe-notifications/country/%s/regions"
)


def test_api_get_foodsecurity_data():
    c = {"global": {"api": {"foodsecurity": API_FOOD_SECURITY}}}
    a = APIService(c)
    result = a.get_foodsecurity_data()
    assert result is not None
    assert len(result.keys()) > 0


def test_api_get_foodsecurity_data_days_ago():
    c = {"global": {"api": {"foodsecurity": API_FOOD_SECURITY}}}
    a = APIService(c)
    result = a.get_foodsecurity_data(days_ago=30)
    assert result is not None
    assert len(result.keys()) > 0


def test_api_get_foodsecurity_data_invalid_url():
    c = {"global": {"api": {"foodsecurity": "https://localhost:12345"}}}
    a = APIService(c)
    result = a.get_foodsecurity_data()
    assert result is not None
    assert len(result.keys()) == 0


def test_api_get_regions_by_country_id():
    c = {"global": {"api": {"country_regions": API_COUNTRY_REGIONS}}}
    a = APIService(c)
    result = a.get_regions_by_country_id(4)
    assert result is not None
    assert len(result) > 0


def test_api_get_regions_by_country_id_not_found():
    c = {"global": {"api": {"country_regions": API_COUNTRY_REGIONS}}}
    a = APIService(c)
    result = a.get_regions_by_country_id(0)
    assert result is not None
    assert len(result) == 0
