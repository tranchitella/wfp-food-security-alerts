import logging
import os
import sys


LOGGING_NAME = 'wfp-food-security-alerts'
LOGGING_FORMAT: str = '%(asctime)s [%(levelname)s] %(message)s'


def setup(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger('%s[%s]' % (LOGGING_NAME, os.getpid()))
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter(LOGGING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
