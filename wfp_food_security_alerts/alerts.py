import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from .api import APIService
from .logger import LoggerMixin
from .population import PopulationService


class AlertService(LoggerMixin):

    _config: dict
    _api: APIService
    _population: PopulationService
    _logger: logging.Logger

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

    def __init__(self, config: dict, api: APIService, population: PopulationService):
        super(AlertService, self).__init__()
        self._config = config
        self._api = api
        self._population = population

    def run(self, dry_run: bool = False) -> List[dict]:
        # get setings from the configuration file
        days_ago = self._config['global']['days_ago']
        threshold = self._config['global']['threshold']
        # get the food security data
        food_security = self._api.get_foodsecurity_data()
        food_security_days_ago = self._api.get_foodsecurity_data(days_ago=days_ago)
        # process the countries defined in the configuration file,
        # and add outgoing notifications to the list
        notifications = []
        countries = self._config.get('countries') or []
        for country in countries:
            self.log_debug("evaluating alerts for country id = %s", country['id'])
            data_not_found = False
            food_security_country = 0
            food_security_days_ago_country = 0
            population_country = 0
            # get the list of regions for the country, for each one...
            regions = self._api.get_regions_by_country_id(country['id'])
            for region_id in regions:
                # get the food security data for the region
                food_security_region = food_security.get(region_id)
                if food_security_region is None:
                    data_not_found = True
                    break
                # get the food security data for the region (N days ago)
                food_security_days_ago_region = food_security_days_ago.get(region_id)
                if food_security_days_ago_region is None:
                    data_not_found = True
                    break
                # get the population from the local data storage
                population_region = self._population.get_population_by_region_id(
                    region_id
                )
                if population_region is None:
                    data_not_found = True
                    break
                # sum up the values for the region in the total for the country
                food_security_days_ago_country += food_security_days_ago_region
                food_security_country += food_security_region
                population_country += population_region
            # if data for one of the regions is not found, skip the country
            if data_not_found is True:
                continue
            # translate absolute numbers to percentages
            p_food_security = (
                float(food_security_country) / float(population_country or 1.0) * 100.0
            )
            p_food_security_days_ago = (
                float(food_security_days_ago_country)
                / float(population_country or 1.0)
                * 100.0
            )
            # evaluate the alert condition
            alert = self.evaluate_alert_condition(
                threshold, p_food_security, p_food_security_days_ago,
            )
            # if the alert is true, create a new notification dictionary and add it
            # to the list of outgoing notifications
            if alert is True:
                notification = {
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
                    "p_food_security_variation": p_food_security
                    - p_food_security_days_ago,
                }
                notifications.append(notification)
                self.log_info("new notification: %r", notification)
        # send the nodifications via SMTP
        if len(notifications) > 0 and not dry_run:
            self.send_notifications(notifications)
        # return the notifications
        return notifications

    def send_notifications(self, notifications: List[dict]):
        # connection to the SMTP server
        smtp_host = self._config['global']['smtp']['host']
        smtp_port = self._config['global']['smtp']['port']
        try:
            s = smtplib.SMTP(host=smtp_host, port=smtp_port)
        except smtplib.SMTPConnectError as e:
            self.log_error("unable to connect to the SMTP server: %s", e)
            return
        # (optional) log in to the SMTP server
        smtp_username = self._config['global']['smtp'].get('username')
        smtp_password = self._config['global']['smtp'].get('password')
        if smtp_username and smtp_password:
            try:
                s.login(smtp_username, smtp_password)
            except smtplib.SMTPAuthenticationError as e:
                self.log_error("unable to log into the SMTP server: %s", e)
                return
        # send the notifications
        for notification in notifications:
            msg = MIMEMultipart()
            msg['From'] = self._config['global']['smtp']['sender']
            msg['To'] = notification['recipients']
            msg['Cc'] = ', '.join(self._config['global']['emails'])
            msg['Subject'] = (
                "Food security decreases significantly in country %(country_id)s"
                % notification
            )
            message = self.NOTIFICATION_TEMPLATE % notification
            msg.attach(MIMEText(message, 'plain'))
            try:
                s.send_message(msg)
            except smtplib.SMTPResponseException as e:
                self.log_error("unable to send the email message: %s", e)
        s.close()

    def evaluate_alert_condition(
        self, threshold: float, p_food_security: float, p_food_security_days_ago: float
    ) -> bool:
        return p_food_security - p_food_security_days_ago >= threshold
