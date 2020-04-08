import yaml
import logging
import requests
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import loads
from operator import itemgetter
from typing import Dict, Optional, Tuple

from .population import PopulationService


GET_FOODSECURITY = 'https://api.hungermapdata.org/swe-notifications/foodsecurity'
GET_REGIONS_BY_COUNTRY_ID = (
    'https://api.hungermapdata.org/swe-notifications/country/%s/regions'
)

NOTIFICATION_TEMPLATE = """Food security decreases significantly in country %(country_id)s.

Population: %(population_country)d

Food security today: %(food_security)d
Food security %(days_ago)d days ago: %(food_security_days_ago)d
Variation: %(food_security_variation)d

%% Food security today: %(p_food_security).2f
%% Food security %(days_ago)d days ago: %(p_food_security_days_ago).2f
%% Variation: %(p_food_security_variation).2f

which is above the threshold of %(threshold).2f

Best regards,
WFP
"""


def send(db_population: str, config: str, logger: Optional[logging.Logger] = None):
    config_data = read_config_file(config, logger=logger)
    if config_data is None:
        return
    db = PopulationService(db_population)
    try:
        evaluate_alerts(config_data, db, logger=logger)
    finally:
        db.close()


def read_config_file(
    config: str, logger: Optional[logging.Logger] = None
) -> Optional[dict]:
    try:
        with open(config) as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        if logger is not None:
            logger.error('Unable to read the config file: %s', e)
        return None
    except yaml.scanner.ScannerError as e:
        if logger is not None:
            logger.error('The provided config file is not a valid YAML: %s', e)
        return None


def evaluate_alerts(
    config: dict, db: PopulationService, logger: Optional[logging.Logger]
):
    days_ago = config['global']['days_ago']
    threshold = config['global']['threshold']
    api_foodsecurity = config['global']['api']['foodsecurity']
    api_country_regions = config['global']['api']['country_regions']
    food_security_days_ago = get_foodsecurity_data(
        api_foodsecurity, days_ago=days_ago, logger=logger
    )
    food_security = get_foodsecurity_data(api_foodsecurity, logger=logger)
    countries = config.get('countries') or []
    notifications = []
    for country in countries:
        if logger is not None:
            logger.debug("Evaluating alerts for country id = %s", country['id'])
        regions = get_regions_by_country_id(
            api_country_regions, country['id'], logger=logger
        )
        data_not_found = False
        food_security_country = 0
        food_security_days_ago_country = 0
        population_country = 0
        for region_id in regions:
            food_security_region = food_security.get(region_id)
            if food_security_region is None:
                data_not_found = True
                break
            food_security_days_ago_region = food_security_days_ago.get(region_id)
            if food_security_days_ago_region is None:
                data_not_found = True
                break
            population_region = db.get_population_by_region_id(region_id)
            if population_region is None:
                data_not_found = True
                break
            food_security_days_ago_country += food_security_days_ago_region
            food_security_country += food_security_region
            population_country += population_region
        if data_not_found is True:
            continue
        p_food_security = (
            float(food_security_country) / float(population_country or 1.0) * 100.0
        )
        p_food_security_days_ago = (
            float(food_security_days_ago_country)
            / float(population_country or 1.0)
            * 100.0
        )
        alert = evaluate_alert_condition(
            threshold, p_food_security, p_food_security_days_ago,
        )
        if alert is False:
            continue
        notifications.append(
            {
                "country_id": country['id'],
                "days_ago": days_ago,
                "threshold": threshold,
                "recipients": ', '.join(country['emails']),
                "population_country": population_country,
                "food_security": food_security_country,
                "food_security_days_ago": food_security_days_ago_country,
                "food_security_variation": food_security_country
                - food_security_days_ago_country,
                "p_food_security": p_food_security,
                "p_food_security_days_ago": p_food_security_days_ago,
                "p_food_security_variation": p_food_security - p_food_security_days_ago,
            }
        )
    if len(notifications) == 0:
        return
    s = smtplib.SMTP(
        host=config['global']['smtp']['host'], port=config['global']['smtp']['port']
    )
    smtp_username = config['global']['smtp'].get('username')
    smtp_password = config['global']['smtp'].get('password')
    if smtp_username and smtp_password:
        s.login(smtp_username, smtp_password)
    for notification in notifications:
        msg = MIMEMultipart()
        msg['From'] = config['global']['smtp']['sender']
        msg['To'] = notification['recipients']
        msg['Cc'] = ', '.join(config['global']['emails'])
        msg['Subject'] = (
            "Food security decreases significantly in country %(country_id)s"
            % notification
        )
        message = NOTIFICATION_TEMPLATE % notification
        msg.attach(MIMEText(message, 'plain'))
        s.send_message(msg)
    s.close()


def evaluate_alert_condition(
    threshold: float, p_food_security: float, p_food_security_days_ago: float
) -> bool:
    return p_food_security - p_food_security_days_ago >= threshold


def get_foodsecurity_data(
    url: str, days_ago: Optional[int] = None, logger: Optional[logging.Logger] = None
) -> Dict[int, int]:
    if days_ago is not None:
        url += '?days_ago=%d' % days_ago
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if logger is not None:
            logger.error('Unable to download the data: %s', e)
        return {}
    data = loads(r.content)
    return dict((x['region_id'], x['food_insecure_people']) for x in data)


def get_regions_by_country_id(
    url: str, country_id: int, logger: Optional[logging.Logger] = None
) -> Tuple[int]:
    url = url % country_id
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if logger is not None:
            logger.error('Unable to download the data: %s', e)
        return Tuple[int](())
    data = loads(r.content)
    regions = data.get('regions') or {}
    return Tuple[int](map(itemgetter('region_id'), regions))
