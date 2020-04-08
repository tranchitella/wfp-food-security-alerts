import yaml
import logging

from typing import Optional


def read_config_file(config: str, logger: logging.Logger = None) -> Optional[dict]:
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
