# WFP food security alerts

The WFP food security alerts software implements an email alerting and notification system for food security.

## Download the data

First of all, the tool needs to download and store locally the data about the population of the regions.
To perform this task you can run the following command:

```bash
$ CSV=https://api.hungermapdata.org/swe-notifications/population.csv
$ wfp-food-security-alerts --db-population=population.sqlite3 --debug download-population $CSV
2020-04-08 07:23:16,682 [DEBUG] Downloading population data from https://api.hungermapdata.org/swe-notifications/population.csv
2020-04-08 07:23:16,980 [DEBUG] Inserted 4288 records into the population database
```

The CLI will create a SQLite database named `population.sqlite` containing the data from the CSV.

## Write your configuration file

The tool needs a configuration file which includes global and country-specific settings; please see the `config.yaml` provided with the source package for an example.

## Run the tool

You can run the tool using the following command

```bash
$ wfp-food-security-alerts --db-population=population.sqlite3 --debug send_alerts --config=config.yaml
```

## Run the tests

This software includes a test suite you can run using the following command:

```bash
$ make test
```

You can also produce test code coverage reports using the following command:

```bash
$ make coverage
```