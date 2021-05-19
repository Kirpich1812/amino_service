import pathlib
import traceback
from functools import partial
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from prettytable import from_db_cursor
import src.paths as paths
from .converter import convert_from_txt
from .database import DatabaseController
from .logger import logger
from .login import login, check_accounts
from .scripts.badass import Badass
from .scripts.bot_management import BotManagement
from .scripts.chat_moderation import ChatModeration
from .scripts.create_accounts import CreateAccounts
from .scripts.single_management import SingleManagement


class ServiceApp:
    def __init__(self):
        while True:
            accounts = DatabaseController().get_auth_data()
            if accounts:
                print("Accounts:")
                for x, account in enumerate(accounts, 1):
                    print(f"{x}. {account[0]}")
                choice = input("\nEnter \"+\" to add an account or \"-\" to delete\n>>> ")
                if choice == "+":
                    email = input("Email: ")
                    password = input("Password: ")
                    DatabaseController().set_auth_data(email, password)
                if choice == "-":
                    delete_choice = input("Enter account number: ")
                    index = int(delete_choice) - 1
                    email = accounts[index][0]
                    DatabaseController().remove_account(email)
                else:
                    index = int(choice) - 1
                    email = accounts[index][0]
                    password = accounts[index][1]
                    break
            if not accounts:
                email = input("Email: ")
                password = input("Password: ")
                DatabaseController().set_auth_data(email, password)
                break

        self.client = login((email, password))
        if not self.client:
            print(colored("Failed login", "red"))
            exit(0)
        logger.debug(f"Login ({email}:{password})")
        print(colored("Login was successful!", "green"))

        subs = self.client.sub_clients(start=0, size=100)
        for x, com_name in enumerate(subs.name, 1):
            print(f"{x}. {com_name}")
        self.sub_client = amino.SubClient(comId=subs.comId[int(input("Enter community number: ")) - 1], client=self.client)
        logger.debug(f"Community {self.sub_client.comId}")

        self.single_management = SingleManagement(self.sub_client)
        self.bot_management = BotManagement(self.sub_client)
        self.chat_moderation = ChatModeration(self.sub_client)
        self.badass = Badass(self.sub_client)

    def run(self):
        while True:
            try:
                print(colored(open(paths.MANAGEMENT_CHOICE_VIEW_PATH, "r").read(), "cyan"))
                management_choice = input("Enter the number >>> ")
                if management_choice == "1":
                    logger.debug("Management choice 1")
                    while True:
                        print(colored(open(paths.SINGLE_MANAGEMENT_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        logger.debug(f"Function choice {choice}")
                        if choice == "1":
                            quiz_link = input("Quiz link: ")
                            object_id = self.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                            self.single_management.play_quiz(object_id)
                            print("[PlayQuiz]: Finish.")
                        elif choice == "2":
                            self.single_management.unfollow_all()
                            print("[UnfollowAll]: Finish.")
                        elif choice == "3":
                            self.single_management.like_recent_blogs()
                            print("[LikeRecentBlogs]: Finish.")
                        elif choice == "4":
                            self.single_management.follow_all()
                            print("[FollowAll]: Finish.")
                        elif choice == "5":
                            self.single_management.get_blocker_users()
                            print("[BlockerUsers]: Finish.")
                        elif choice == "6":
                            count = input("Number of coins: ")
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            self.single_management.send_coins(int(count), object_id)
                            print("[SendCoins]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "2":
                    logger.debug("Management choice 2")
                    check_accounts()
                    pool = ThreadPool(int(input("Number of threads: ")))
                    while True:
                        print(colored(open(paths.BOT_MANAGEMENT_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        logger.debug(f"Function choice {choice}")
                        if choice == "s":
                            logger.debug("Management choice s")
                            bots = DatabaseController().get_bots_cursor()
                            if bots:
                                mytable = from_db_cursor(bots)
                                print(mytable)
                            else:
                                print(colored("No bots found in the database", "red"))
                        elif choice == "1":
                            result = pool.map(self.bot_management.play_lottery, DatabaseController().get_bots())
                            total_count = 0
                            total_accounts = 0
                            for i in result:
                                if type(i) == int:
                                    total_accounts += 1
                                    total_count += i
                            print(f"Accounts: {total_accounts}\nResult: +{total_count} coins")
                            print("[PlayLottery]: Finish.")
                        elif choice == "2":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            result = pool.map(partial(self.bot_management.send_coins, object_id), DatabaseController().get_bots())
                            total_count = 0
                            total_accounts = 0
                            for i in result:
                                if type(i) == int:
                                    total_accounts += 1
                                    total_count += i
                            print(f"Accounts {total_accounts}\nResult: +{total_count} coins")
                            print("[SendCoins]: Finish.")
                        elif choice == "3":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.like_blog, object_id), DatabaseController().get_bots())
                            print("[LikeBlog]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.join_bots_to_chat, object_id), DatabaseController().get_bots())
                            print("[JoinBotsToChat]: Finish.")
                        elif choice == "5":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.leave_bots_from_chat, object_id), DatabaseController().get_bots())
                            print("[LeaveBotsFromChat]: Finish.")
                        elif choice == "6":
                            subs = self.client.sub_clients(start=0, size=100)
                            for x, com_name in enumerate(subs.name, 1):
                                print(f"{x}. {com_name}")
                            object_id = subs.comId[int(input("Enter community number: ")) - 1]
                            invite_link = None
                            if self.client.get_community_info(object_id).joinType == 2:
                                invite_link = input("Enter invite link/code: ")
                            pool.map(partial(self.bot_management.join_bots_to_community, invite_link), DatabaseController().get_bots())
                            print("[JoinBotsToCommunity]: Finish.")
                        elif choice == "7":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            text = input("Message text: ")
                            pool.map(partial(self.bot_management.send_message, object_id, text), DatabaseController().get_bots())
                            print("[SendMessage]: Finish.")
                        elif choice == "8":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.follow, object_id), DatabaseController().get_bots())
                            print("[Follow]: Finish.")
                        elif choice == "9":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.unfollow, object_id), DatabaseController().get_bots())
                            print("[Unfollow]: Finish.")
                        elif choice == "10":
                            pool.map(self.bot_management.set_online_status, DatabaseController().get_bots())
                            print("[SetOnlineStatus]: Finish.")
                        elif choice == "11":
                            print("1 - Random nick")
                            print("2 - Set custom nick")
                            mode = input("Select mode: ")
                            if mode == "1":
                                max_length = int(input("Max nick length: "))
                                pool.map(partial(self.bot_management.change_nick_random, max_length, None), DatabaseController().get_bots())
                            else:
                                nick = input("Enter nick: ")
                                pool.map(partial(self.bot_management.change_nick_random, None, nick), DatabaseController().get_bots())
                            print("[ChangeNickname]: Finish.")
                        elif choice == "12":
                            user_link = input("User link: ")
                            userid = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            text = input("Text: ")
                            pool.map(partial(self.bot_management.wall_comment, userid, text), DatabaseController().get_bots())
                            print("[WallComment]: Finish.")
                        elif choice == "13":
                            images = []
                            currentDirectory = pathlib.Path(paths.ICONS_PATH)
                            for currentFile in currentDirectory.iterdir():
                                images.append(str(currentFile).split("\\")[2])
                            if images:
                                pool.map(partial(self.bot_management.change_icon_random, images), DatabaseController().get_bots())
                            else:
                                print(colored("icons is empty", "red"))
                            print("[ChangeIcon]: Finish.")
                        elif choice == "14":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            polls = self.sub_client.get_blog_info(blogId=object_id).json["blog"]["polloptList"]
                            for x, i in enumerate(polls, 1):
                                print(f"{x}. {i.get('title')}")
                            option = polls[int(input("Select option number: ")) - 1]["polloptId"]
                            pool.map(partial(self.bot_management.vote_poll, object_id, option), DatabaseController().get_bots())
                            print("[Vote]: Finish.")
                        elif choice == "15":
                            object_link = input("User link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.start_chat, object_id), DatabaseController().get_bots())
                            print("[StartChat]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "3":
                    logger.debug("Management choice 3")
                    while True:
                        print(colored(open(paths.CHAT_MODERATION_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        logger.debug(f"Function choice {choice}")
                        if choice == "1":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            count = input("Number of messages: ")
                            self.chat_moderation.clear_chat(object_id, int(count))
                            print("[ClearChat]: Finish.")
                        elif choice == "2":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.chat_moderation.save_chat_settings(object_id)
                            print("[SaveChatSettings]: Finish.")
                        elif choice == "3":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.chat_moderation.set_view_mode(object_id)
                            print("[SetViewMode]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            duration = int(input("Duration in seconds: "))
                            self.chat_moderation.set_view_mode_timer(object_id, duration)
                            print("[SetViewMode]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "4":
                    logger.debug("Management choice 4")
                    while True:
                        print(colored(open(paths.BADASS_VIEW_PATH, "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        logger.debug(f"Function choice {choice}")
                        if choice == "1":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.send_system_message(object_id)
                            print("[SendSystem]: Finish.")
                        elif choice == "2":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.spam_system_message(object_id)
                            print("[SpamSystem]: Finish.")
                        elif choice == "3":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.delete_chat(object_id)
                            print("[DeleteChat]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.invite_all_users(object_id)
                            print("[InviteAll]: Finish.")
                        elif choice == "5":
                            self.badass.spam_posts()
                            print("[SpamPosts]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "5":
                    logger.debug("Management choice 5")
                    CreateAccounts().run()
                elif management_choice == "0":
                    logger.debug("Management choice 0")
                    convert_from_txt()
                elif management_choice == "d":
                    logger.debug("Management choice d")
                    email = input("Bot login: ")
                    DatabaseController().remove_bot(email)
            except Exception as e:
                print(colored(str(e), "red"))
                logger.debug(traceback.format_exc())
