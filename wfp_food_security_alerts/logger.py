import logging
import os
import sys

from typing import Optional


LOGGING_NAME = 'wfp-food-security-alerts'
LOGGING_FORMAT: str = '%(asctime)s [%(levelname)s] %(message)s'


class LoggerMixin(object):

    _logger: Optional[logging.Logger]

    def __init__(self):
        self._logger = None

    def set_logger(self, logger: logging.Logger):
        self._logger = logger

    def log_debug(self, *args, **kw):
        if self._logger is not None:
            self._logger.debug(*args, **kw)

    def log_info(self, *args, **kw):
        if self._logger is not None:
            self._logger.info(*args, **kw)

    def log_warning(self, *args, **kw):
        if self._logger is not None:
            self._logger.warning(*args, **kw)

    def log_error(self, *args, **kw):
        if self._logger is not None:
            self._logger.error(*args, **kw)


def setup(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger('%s[%s]' % (LOGGING_NAME, os.getpid()))
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter(LOGGING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
