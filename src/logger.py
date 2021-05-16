import logging

from src.database import DatabaseController

logger = logging.getLogger('amino_service')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)d]: %(message)s')
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh)

if DatabaseController().get_bots():
    spaces = max([len(i[0]) for i in DatabaseController().get_bots()])


def service_log(email: str, action: str):
    print("[" + email + " " * spaces + "]: " + action)
