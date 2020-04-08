# Objective

You’re analysing the situation of food security in several countries, each made of several regions. You need to build a python system that runs daily and alerts in case food security decreases significantly in a country (that is, if the percentage of food insecure people in a country increases of >= 5% compared to 30 days ago).

When triggering a notification for a country, an email needs to be sent to a list of recipients (specific for that country) AND to a special admin email address (same address for all the countries). The actual smtp server used for the email is not important (‘fake.smtp.wfp.org’ would do).

## Data sources

* The total population per region is available in a static remote csv file, updated yearly ( https://api.hungermapdata.org/swe-notifications/population.csv )

* Food security (expressed as total number of food-insecure people in each region) is available in a REST API

    * GET https://api.hungermapdata.org/swe-notifications/foodsecurity returns a list of results (one per region), each containing the id of the region and the number of food insecure people

    * The API above accepts an optional query parameter ‘days_ago’ to retrieve past data

* The parent-child relationship between countries and regions is available in a simple REST API:

    * GET https://api.hungermapdata.org/swe-notifications/region/{region_id}/country
    returns country information for a given region

    * GET https://api.hungermapdata.org/swe-notifications/country/{country_id}/regions
    returns the list of regions for a given country

* The list of recipients for each country is part of the configuration of the system (you can decide how and where to store it). Also, the special admin email address is part of the system configuration.