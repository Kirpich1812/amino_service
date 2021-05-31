import pathlib
import traceback
from functools import partial
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from prettytable import from_db_cursor
import src.utils.paths as paths
from src.utils.converter import convert_from_txt
from src.utils.database import DatabaseController
from src.utils.logger import logger, file_logger
from src.utils.login import login, check_accounts
from .scripts.badass import Badass
from .scripts.bot_management import BotManagement
from .scripts.chat_moderation import ChatModeration
from .scripts.create_accounts import CreateAccounts
from .scripts.single_management import SingleManagement
from .utils.chat_menu import get_chat_id


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
        for x, com_name in enumerate(subs.name, 1):
            logger.info(f"{x}. {com_name}")
        self.sub_client = amino.SubClient(comId=subs.comId[int(input("Enter community number: ")) - 1], client=self.client)

        self.single_management = SingleManagement(self.sub_client)
        self.bot_management = BotManagement(self.sub_client)
        self.chat_moderation = ChatModeration(self.sub_client)
        self.badass = Badass(self.sub_client)

    def run(self):
        while True:
            try:
                logger.info(colored(open(paths.MANAGEMENT_CHOICE_VIEW_PATH, "r").read(), "cyan"))
                management_choice = input("Enter the number >>> ")
                if management_choice == "1":
                    while True:
                        logger.info(colored(open(paths.SINGLE_MANAGEMENT_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            quiz_link = input("Quiz link: ")
                            object_id = self.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                            self.single_management.play_quiz(object_id)
                        elif choice == "2":
                            self.single_management.unfollow_all()
                        elif choice == "3":
                            self.single_management.like_recent_blogs()
                        elif choice == "4":
                            self.single_management.follow_all()
                        elif choice == "5":
                            self.single_management.get_blocker_users()
                        elif choice == "6":
                            count = input("Number of coins: ")
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            self.single_management.send_coins(int(count), object_id)
                        elif choice == "b":
                            break
                elif management_choice == "2":
                    check_accounts()
                    pool = ThreadPool(int(input("Number of threads: ")))
                    while True:
                        logger.info(colored(open(paths.BOT_MANAGEMENT_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "s":
                            bots = self.database.get_bots_cursor()
                            if bots:
                                mytable = from_db_cursor(bots)
                                logger.info(mytable)
                            else:
                                logger.error("No bots found in the database")
                        elif choice == "1":
                            result = pool.map(self.bot_management.play_lottery, self.database.get_bots())
                            total_count = 0
                            total_accounts = 0
                            for i in result:
                                if type(i) == int:
                                    total_accounts += 1
                                    total_count += i
                            logger.info(f"Accounts: {total_accounts}\nResult: +{total_count} coins")
                        elif choice == "2":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            result = pool.map(partial(self.bot_management.send_coins, object_id), self.database.get_bots())
                            total_count = 0
                            total_accounts = 0
                            for i in result:
                                if type(i) == int:
                                    total_accounts += 1
                                    total_count += i
                            logger.info(f"Accounts {total_accounts}\nResult: +{total_count} coins")
                        elif choice == "3":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.like_blog, object_id), self.database.get_bots())
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.join_bots_to_chat, object_id), self.database.get_bots())
                        elif choice == "5":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.leave_bots_from_chat, object_id), self.database.get_bots())
                        elif choice == "6":
                            subs = self.client.sub_clients(start=0, size=100)
                            for x, com_name in enumerate(subs.name, 1):
                                logger.info(f"{x}. {com_name}")
                            object_id = subs.comId[int(input("Enter community number: ")) - 1]
                            invite_link = None
                            if self.client.get_community_info(object_id).joinType == 2:
                                invite_link = input("Enter invite link/code: ")
                            pool.map(partial(self.bot_management.join_bots_to_community, invite_link), self.database.get_bots())
                        elif choice == "7":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            text = input("Message text: ")
                            pool.map(partial(self.bot_management.send_message, object_id, text), self.database.get_bots())
                        elif choice == "8":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.follow, object_id), self.database.get_bots())
                        elif choice == "9":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.unfollow, object_id), self.database.get_bots())
                        elif choice == "10":
                            pool.map(self.bot_management.set_online_status, self.database.get_bots())
                        elif choice == "11":
                            logger.info("1 - Random nick")
                            logger.info("2 - Set custom nick")
                            mode = input("Select mode: ")
                            if mode == "1":
                                max_length = int(input("Max nick length: "))
                                pool.map(partial(self.bot_management.change_nick_random, max_length, None), self.database.get_bots())
                            else:
                                nick = input("Enter nick: ")
                                pool.map(partial(self.bot_management.change_nick_random, None, nick), self.database.get_bots())
                        elif choice == "12":
                            user_link = input("User link: ")
                            userid = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            text = input("Text: ")
                            pool.map(partial(self.bot_management.wall_comment, userid, text), self.database.get_bots())
                        elif choice == "13":
                            images = []
                            currentDirectory = pathlib.Path(paths.ICONS_PATH)
                            for currentFile in currentDirectory.iterdir():
                                images.append(str(currentFile).split("\\")[2])
                            if images:
                                pool.map(partial(self.bot_management.change_icon_random, images), self.database.get_bots())
                            else:
                                logger.error("icons is empty")
                        elif choice == "14":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            polls = self.sub_client.get_blog_info(blogId=object_id).json["blog"]["polloptList"]
                            for x, i in enumerate(polls, 1):
                                logger.info(f"{x}. {i.get('title')}")
                            option = polls[int(input("Select option number: ")) - 1]["polloptId"]
                            pool.map(partial(self.bot_management.vote_poll, object_id, option), self.database.get_bots())
                        elif choice == "15":
                            object_link = input("User link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.start_chat, object_id), self.database.get_bots())
                        elif choice == "b":
                            break
                elif management_choice == "3":
                    while True:
                        logger.info(colored(open(paths.CHAT_MODERATION_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            self.chat_moderation.clear_chat(get_chat_id(self.sub_client))
                        elif choice == "2":
                            self.chat_moderation.save_chat_settings(get_chat_id(self.sub_client))
                        elif choice == "3":
                            self.chat_moderation.set_view_mode(get_chat_id(self.sub_client))
                        elif choice == "4":
                            self.chat_moderation.set_view_mode_timer(get_chat_id(self.sub_client))
                        elif choice == "b":
                            break
                elif management_choice == "4":
                    while True:
                        logger.info(colored(open(paths.BADASS_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            self.badass.send_system_message(get_chat_id(self.sub_client))
                        elif choice == "2":
                            self.badass.spam_system_message(get_chat_id(self.sub_client))
                        elif choice == "3":
                            self.badass.delete_chat(get_chat_id(self.sub_client))
                        elif choice == "4":
                            self.badass.invite_all_users(get_chat_id(self.sub_client))
                        elif choice == "5":
                            self.badass.spam_posts()
                        elif choice == "b":
                            break
                elif management_choice == "5":
                    CreateAccounts().run()
                elif management_choice == "0":
                    convert_from_txt()
                elif management_choice == "d":
                    email = input("Bot email: ")
                    self.database.remove_bot(email)
                    logger.info(f"{email} removed from the database")
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())
