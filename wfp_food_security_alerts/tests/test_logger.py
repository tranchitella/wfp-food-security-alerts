import logging

from wfp_food_security_alerts import logger


def test_logging_setup():
    lg = logger.setup(True)
    assert lg is not None
    assert type(lg) is logging.Logger
    assert lg.level == logging.DEBUG


def test_logging_mixin():
    lg = logger.setup(False)
    obj = logger.LoggerMixin()
    obj.set_logger(lg)
    obj.log_debug("")
    obj.log_info("")
    obj.log_warning("")
    obj.log_error("")
