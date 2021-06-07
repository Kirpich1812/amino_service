import traceback

from termcolor import colored

import amino
from src.utils.converter import convert_from_txt
from src.utils.database import DatabaseController
from src.utils.logger import logger, file_logger
from src.utils.login import login
from src.scripts.badass import Badass
from src.scripts.bot_management import BotManagement
from src.scripts.chat_moderation import ChatModeration
from src.scripts.create_accounts import CreateAccounts
from src.scripts.single_management import SingleManagement
from src.utils.configs import MAIN_MENU
from src.utils.table import create_table


class ServiceApp:
    def __init__(self):
        self.database = DatabaseController()
        while True:
            accounts = self.database.get_auth_data()
            if accounts:
                logger.info("Accounts:")
                for x, account in enumerate(accounts, 1):
                    logger.info(f"{x}. {account[0]}")
                choice = input("\n" + "Enter \"+\" to add an account or \"-\" to delete " + "\n" + ">>> ")
                if choice == "+":
                    email = input("Email: ")
                    password = input("Password: ")
                    self.database.set_auth_data(email, password)
                elif choice == "-":
                    delete_choice = input("Enter account number: ")
                    index = int(delete_choice) - 1
                    email = accounts[index][0]
                    self.database.remove_account(email)
                else:
                    index = int(choice) - 1
                    email = accounts[index][0]
                    password = accounts[index][1]
                    break
            if not accounts:
                email = input("Email: ")
                password = input("Password: ")
                self.database.set_auth_data(email, password)
                break

        self.client = login((email, password))
        if not self.client:
            exit(0)
        logger.info("Login was successful!")

        subs = self.client.sub_clients(start=0, size=100)
        if subs.comId:
            for x, com_name in enumerate(subs.name, 1):
                logger.info(f"{x}. {com_name}")
            com_index = int(input("Enter community number: "))
            self.sub_client = amino.SubClient(comId=subs.comId[com_index - 1], client=self.client)
        else:
            logger.error("Join at least one community")
            exit(0)

    def run(self):
        while True:
            try:
                logger.info(colored(create_table("Menu", MAIN_MENU), "cyan"))
                management_choice = input("Select action >>> ")
                if management_choice == "1":
                    SingleManagement(self.sub_client)
                if management_choice == "2":
                    BotManagement(self.sub_client)
                if management_choice == "3":
                    ChatModeration(self.sub_client)
                if management_choice == "4":
                    Badass(self.sub_client)
                if management_choice == "5":
                    CreateAccounts().run()
                if management_choice == "0":
                    convert_from_txt()
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())
