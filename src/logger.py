from src.other import get_accounts
import logging

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

spaces = max([len(i) for i in get_accounts()])


def service_log(email: str, action: str):
    print("[" + email + " " * spaces + "]: " + action)
