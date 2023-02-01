import logging

LOGGER_NAME = "app"


def get_logger(logger_name: str) -> logging.Logger:

    from rich.logging import RichHandler

    rich_handler = RichHandler(
        show_time=False, rich_tracebacks=False, tracebacks_show_locals=False
    )
    rich_handler.setFormatter(
        logging.Formatter(
            fmt="%(message)s",
            datefmt="[%X]",
        )
    )

    _logger = logging.getLogger(logger_name)
    _logger.addHandler(rich_handler)
    _logger.setLevel(logging.INFO)
    return _logger


def set_log_level_to_debug():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)


logger: logging.Logger = get_logger(LOGGER_NAME)
