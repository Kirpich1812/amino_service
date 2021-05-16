import os

from src.database import DatabaseController


def convert_from_txt():
    bots = open(os.path.join(os.getcwd(), "src", "bots.txt"), "r").readlines()
    accounts = []
    if bots:
        for i in bots:
            split = i.replace(" ", "").replace("\n", "").split(":")
            accounts.append({"email": split[0], "password": split[1]})
        DatabaseController().set_bots(accounts)
