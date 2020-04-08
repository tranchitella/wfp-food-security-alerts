# WFP food security alerts

The WFP food security alerts software implements an email alerting and notification system for food security.

## Download the data

First of all, the tool needs to download and store locally the data about the population of the regions.
To perform this task, you can run the following command:

```bash
$ CSV=https://api.hungermapdata.org/swe-notifications/population.csv
$ wfp-food-security-alerts --db-population=population.sqlite3 --debug download-population $CSV
2020-04-08 07:23:16,682 [DEBUG] Downloading population data from https://api.hungermapdata.org/swe-notifications/population.csv
2020-04-08 07:23:16,980 [DEBUG] Inserted 4288 records into the population database
```

The CLI will create a SQLite database named `population.sqlite` containing the data from the CSV.

You can manually inspect the database:

```bash
$ sqlite3 population.sqlite3
sqlite> select * from population limit 10;
0|0
272|1241185
273|656495
274|970010
275|1312520
276|509567
277|630514
278|1202486
279|856963
280|829953
```

## Write your configuration file

The tool needs a configuration file which includes global and country-specific settings; please see the `config.yaml` provided with the source package for an example, as it contains comments which explain the different settings.

## Run the tool

You can run the tool using the following command

```bash
$ wfp-food-security-alerts --db-population=population.sqlite3 --debug send_alerts --config=config.yaml
```

If you want to run the tool without sending the email messages, you can add the `--dry-run` option as follows:

```bash
$ wfp-food-security-alerts --db-population=population.sqlite3 --debug send_alerts --config=config.yaml --dry-run
```

## Run the tests

This software includes a test suite you can run using the following command:

```bash
$ make test
================================================ test session starts =================================================
platform darwin -- Python 3.8.1, pytest-5.4.1, py-1.8.1, pluggy-0.13.1
rootdir: /Users/kobold/src/wfp-food-security-alerts
collected 16 items

wfp_food_security_alerts/tests/test_alerts.py ....                                                             [ 25%]
wfp_food_security_alerts/tests/test_api.py .....                                                               [ 56%]
wfp_food_security_alerts/tests/test_config.py ...                                                              [ 75%]
wfp_food_security_alerts/tests/test_logger.py ..                                                               [ 87%]
wfp_food_security_alerts/tests/test_population.py ..                                                           [100%]

================================================= 16 passed in 1.33s =================================================
```

You can also produce test code coverage reports using the following command:

```bash
$ make coverage
================================================ test session starts =================================================
platform darwin -- Python 3.8.1, pytest-5.4.1, py-1.8.1, pluggy-0.13.1
rootdir: /Users/kobold/src/wfp-food-security-alerts
collected 16 items

wfp_food_security_alerts/tests/test_alerts.py ....                                                             [ 25%]
wfp_food_security_alerts/tests/test_api.py .....                                                               [ 56%]
wfp_food_security_alerts/tests/test_config.py ...                                                              [ 75%]
wfp_food_security_alerts/tests/test_logger.py ..                                                               [ 87%]
wfp_food_security_alerts/tests/test_population.py ..                                                           [100%]

================================================= 16 passed in 1.37s =================================================
coverage report
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
wfp_food_security_alerts/__init__.py         0      0   100%
wfp_food_security_alerts/alerts.py          81     22    73%
wfp_food_security_alerts/api.py             34      0   100%
wfp_food_security_alerts/cli.py             47     47     0%
wfp_food_security_alerts/config.py          15      2    87%
wfp_food_security_alerts/logger.py          33      0   100%
wfp_food_security_alerts/population.py      58      7    88%
------------------------------------------------------------
TOTAL                                      268     78    71%
```