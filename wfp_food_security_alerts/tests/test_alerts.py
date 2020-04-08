from wfp_food_security_alerts.alerts import AlertService
from wfp_food_security_alerts.api import APIService
from wfp_food_security_alerts.population import PopulationService


class MockedAPIService:
    def __init__(
        self, foodsecurity_data: dict, foodsecurity_data_days_ago: dict, regions: dict
    ):
        self._foodsecurity_data = foodsecurity_data
        self._foodsecurity_data_days_ago = foodsecurity_data_days_ago
        self._regions = regions

    def get_foodsecurity_data(self, days_ago: int = None):
        return (
            self._foodsecurity_data
            if days_ago is None
            else self._foodsecurity_data_days_ago
        )

    def get_regions_by_country_id(self, country_id: int):
        return self._regions


class MockedPopulationService:
    def __init__(self, population: dict):
        self._population = population

    def get_population_by_region_id(self, region_id: int):
        return self._population[region_id]


def test_evaluate_alert_condition_true(tmpdir):
    c = {}
    a = APIService(c)
    p = PopulationService()
    result = AlertService(c, a, p).evaluate_alert_condition(10, 100, 90)
    assert result is True


def test_evaluate_alert_condition_false(tmpdir):
    c = {}
    a = APIService(c)
    p = PopulationService()
    result = AlertService(c, a, p).evaluate_alert_condition(10, 100, 95)
    assert result is False


def test_run_notification():
    c = {
        "countries": [{"id": 1, "emails": ["email@example.org"]}],
        "global": {"threshold": 10.0, "days_ago": 30, "emails": ["admin@example.org"]},
    }
    a = MockedAPIService(
        foodsecurity_data={100: 100},
        foodsecurity_data_days_ago={100: 90},
        regions=[100],
    )
    p = MockedPopulationService(population={100: 100})
    svc = AlertService(c, a, p)
    notifications = svc.run(dry_run=True)
    assert notifications == [
        {
            'country_id': 1,
            'days_ago': 30,
            'food_security': 100,
            'food_security_days_ago': 90,
            'food_security_variation': 10,
            'p_food_security': 100.0,
            'p_food_security_days_ago': 90.0,
            'p_food_security_variation': 10.0,
            'population_country': 100,
            'recipients': 'email@example.org',
            'threshold': 10.0,
        },
    ]


def test_run_notification_not_triggered():
    c = {
        "countries": [{"id": 1, "emails": ["email@example.org"]}],
        "global": {"threshold": 10.0, "days_ago": 30, "emails": ["admin@example.org"]},
    }
    a = MockedAPIService(
        foodsecurity_data={100: 100},
        foodsecurity_data_days_ago={100: 90},
        regions=[1000],
    )
    p = MockedPopulationService(population={100: 100})
    svc = AlertService(c, a, p)
    notifications = svc.run(dry_run=True)
    assert notifications == []
