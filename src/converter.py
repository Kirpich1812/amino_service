import os

from termcolor import colored

from src.database import DatabaseController
from src.paths import BOTS_TXT_PATH


def convert_from_txt():
    if not os.path.exists(os.path.join(BOTS_TXT_PATH)):
        print(colored(BOTS_TXT_PATH + " not found", "red"))
        return
    bots = open(BOTS_TXT_PATH, "r").readlines()
    accounts = []
    if bots:
        for i in bots:
            split = i.replace(" ", "").replace("\n", "").split(":")
            try:
                accounts.append({"email": split[0], "password": split[1]})
            except IndexError:
                pass
        DatabaseController().set_bots(accounts)
