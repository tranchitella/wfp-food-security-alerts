import requests

from json import loads
from operator import itemgetter
from typing import Dict, Optional

from .logger import LoggerMixin


class APIService(LoggerMixin):

    _config: dict

    def __init__(self, config: dict):
        super(APIService, self).__init__()
        self._config = config

    def get_foodsecurity_data(self, days_ago: Optional[int] = None) -> Dict[int, int]:
        url = self._config['global']['api']['foodsecurity']
        if days_ago is not None:
            url += '?days_ago=%d' % days_ago
        try:
            r = requests.get(url)
            r.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as e:
            self.log_error('unable to download the data from API %s', e)
            return {}
        data = loads(r.content)
        return dict((x['region_id'], x['food_insecure_people']) for x in data)

    def get_regions_by_country_id(self, country_id: int) -> tuple:
        url = self._config['global']['api']['country_regions']
        url = url % country_id
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.log_error('unable to download the data from API: %s', e)
            return tuple()
        data = loads(r.content)
        regions = data.get('regions') or {}
        return tuple(map(itemgetter('region_id'), regions))
