from wfp_food_security_alerts import alerts


def test_evaluate_alert_condition_true(tmpdir):
    result = alerts.evaluate_alert_condition(10, 100, 90)
    assert result is True


def test_evaluate_alert_condition_false(tmpdir):
    result = alerts.evaluate_alert_condition(10, 100, 95)
    assert result is False
