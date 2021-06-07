import logging
import sys
import traceback

import coloredlogs

from src.utils.database import DatabaseController

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
file_logger = logging.getLogger('file_logger')
file_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = coloredlogs.ColoredFormatter(fmt="%(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('log.log', encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(fmt='[%(asctime)s][%(filename)s:%(lineno)d]: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)


if DatabaseController().get_bots():
    spaces = max([len(i[0]) for i in DatabaseController().get_bots()])
else:
    spaces = 25


def service_align(email: str, action: str):
    return "[" + email + " " * spaces + "]: " + action


def exception_handler(func):
    def wrapper(*args):
        try:
            func(*args)
        except Exception as e:
            error_message = e.args[0]
            if isinstance(error_message, str):
                logger.error(error_message)
                file_logger.debug(traceback.format_exc())
            if isinstance(error_message, dict):
                if isinstance(args[-1], tuple):
                    logger.error(service_align(args[-1][0], error_message["api:message"]))
                else:
                    logger.error(error_message["api:message"])
    return wrapper
