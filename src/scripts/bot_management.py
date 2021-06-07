import os
import pathlib
import random
import traceback
from functools import partial
from multiprocessing.pool import ThreadPool

from prettytable import from_db_cursor
from termcolor import colored

import amino
from src.utils import configs
from src.utils.database import DatabaseController
from src.utils.logger import service_align, exception_handler, logger, file_logger
from src.utils.login import login_sid, check_accounts
from src.utils.nick_gen import UsernameGenerator
from src.utils.configs import ICONS_PATH, BOTS_MANAGEMENT_MENU
from src.utils.table import create_table


class BotManagement:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client
        self.com_id = self.sub_client.comId
        self.database = DatabaseController()
        check_accounts()
        pool = ThreadPool(int(input("Number of threads: ")))
        while True:
            try:
                logger.info(colored(create_table("Bots Management", BOTS_MANAGEMENT_MENU), "cyan"))
                choice = input("Select action >>> ")
                if choice == "s":
                    bots = self.database.get_bots_cursor()
                    if bots:
                        logger.info(from_db_cursor(bots))
                    else:
                        logger.error("No bots found in the database")
                if choice == "d":
                    email = input("Bot email: ")
                    self.database.remove_bot(email)
                    logger.info(f"{email} removed from the database")
                if choice == "1":
                    result = pool.map(self.play_lottery, self.database.get_bots())
                    total_count, total_accounts = 0, 0
                    for i in result:
                        if type(i) == int:
                            total_accounts += 1
                            total_count += i
                    logger.info(f"Accounts: {total_accounts}\nResult: +{total_count} coins")
                if choice == "2":
                    blog_link = input("Blog link: ")
                    object_id = self.sub_client.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    result = pool.map(partial(self.send_coins, object_id), self.database.get_bots())
                    total_count, total_accounts = 0, 0
                    for i in result:
                        if type(i) == int:
                            total_accounts += 1
                            total_count += i
                    logger.info(f"Accounts {total_accounts}\nResult: +{total_count} coins")
                if choice == "3":
                    blog_link = input("Blog link: ")
                    object_id = self.sub_client.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    pool.map(partial(self.like_blog, object_id), self.database.get_bots())
                if choice == "4":
                    object_link = input("Link: ")
                    object_id = self.sub_client.client.get_from_code(str(object_link.split('/')[-1])).objectId
                    pool.map(partial(self.join_bots_to_chat, object_id), self.database.get_bots())
                if choice == "5":
                    object_link = input("Link: ")
                    object_id = self.sub_client.client.get_from_code(str(object_link.split('/')[-1])).objectId
                    pool.map(partial(self.leave_bots_from_chat, object_id), self.database.get_bots())
                if choice == "6":
                    subs = self.sub_client.client.sub_clients(start=0, size=100)
                    for x, com_name in enumerate(subs.name, 1):
                        logger.info(f"{x}. {com_name}")
                    object_id = subs.comId[int(input("Enter community number: ")) - 1]
                    invite_link = None
                    if self.sub_client.client.get_community_info(object_id).joinType == 2:
                        invite_link = input("Enter invite link/code: ")
                    pool.map(partial(self.join_bots_to_community, invite_link), self.database.get_bots())
                if choice == "7":
                    object_link = input("Link: ")
                    object_id = self.sub_client.client.get_from_code(str(object_link.split('/')[-1])).objectId
                    text = input("Message text: ")
                    pool.map(partial(self.send_message, object_id, text), self.database.get_bots())
                if choice == "8":
                    user_link = input("Link to user: ")
                    object_id = self.sub_client.client.get_from_code(str(user_link.split('/')[-1])).objectId
                    pool.map(partial(self.follow, object_id), self.database.get_bots())
                if choice == "9":
                    user_link = input("Link to user: ")
                    object_id = self.sub_client.client.get_from_code(str(user_link.split('/')[-1])).objectId
                    pool.map(partial(self.unfollow, object_id), self.database.get_bots())
                if choice == "10":
                    logger.info("1 - Random nick")
                    logger.info("2 - Set custom nick")
                    mode = input("Select mode: ")
                    if mode == "1":
                        max_length = int(input("Max nick length: "))
                        pool.map(partial(self.change_nick_random, max_length, None),
                                 self.database.get_bots())
                    else:
                        nick = input("Enter nick: ")
                        pool.map(partial(self.change_nick_random, None, nick), self.database.get_bots())
                if choice == "11":
                    user_link = input("User link: ")
                    userid = self.sub_client.client.get_from_code(str(user_link.split('/')[-1])).objectId
                    text = input("Text: ")
                    pool.map(partial(self.wall_comment, userid, text), self.database.get_bots())
                if choice == "12":
                    current_directory = pathlib.Path(configs.ICONS_PATH)
                    images = [x.name for x in current_directory.iterdir()]
                    if images:
                        pool.map(partial(self.change_icon_random, images), self.database.get_bots())
                    else:
                        logger.error("icons is empty")
                if choice == "13":
                    blog_link = input("Blog link: ")
                    object_id = self.sub_client.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    polls = self.sub_client.get_blog_info(blogId=object_id).json["blog"]["polloptList"]
                    for x, i in enumerate(polls, 1):
                        logger.info(f"{x}. {i.get('title')}")
                    option = polls[int(input("Select option number: ")) - 1]["polloptId"]
                    pool.map(partial(self.vote_poll, object_id, option), self.database.get_bots())
                if choice == "14":
                    object_link = input("User link: ")
                    object_id = self.sub_client.client.get_from_code(str(object_link.split('/')[-1])).objectId
                    pool.map(partial(self.start_chat, object_id), self.database.get_bots())
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    @exception_handler
    def play_lottery(self, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        play = sub_client.lottery()
        award = play.awardValue if play.awardValue else 0
        logger.info(service_align(email, f"+{award} coins won"))
        return int(award)

    @exception_handler
    def send_coins(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        coins = int(client.get_wallet_info().totalCoins)
        if coins != 0:
            sub_client.send_coins(coins=coins, blogId=object_id)
            logger.info(service_align(email, f"+{coins} coins"))
            return coins
        else:
            logger.info(service_align(email, f"NotEnoughCoins"))

    @exception_handler
    def like_blog(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.like_blog(blogId=object_id)
        logger.info(service_align(email, "Like"))

    @exception_handler
    def join_bots_to_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.join_chat(chatId=object_id)
        logger.info(service_align(email, "Join"))

    @exception_handler
    def leave_bots_from_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.leave_chat(chatId=object_id)
        logger.info(service_align(email, "Leave"))

    @exception_handler
    def join_bots_to_community(self, inv_link=None, account: tuple = None):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        invitation_id = None
        if inv_link:
            invitation_id = client.link_identify(code=str(inv_link.split("/")[-1])).get("invitationId")
        if invitation_id:
            client.join_community(comId=self.com_id, invitationId=invitation_id)
            logger.info(service_align(email, "Join"))
        if invitation_id is None:
            client.join_community(comId=self.com_id)
            logger.info(service_align(email, "Join"))

    @exception_handler
    def send_message(self, object_id, text, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.send_message(chatId=object_id, message=text)
        logger.info(service_align(email, "Send"))

    @exception_handler
    def follow(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.follow(userId=object_id)
        logger.info(service_align(email, "Follow"))

    @exception_handler
    def unfollow(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.unfollow(userId=object_id)
        logger.info(service_align(email, "Unfollow"))

    @exception_handler
    def start_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.start_chat(userId=object_id, message="")
        logger.info(service_align(email, "Started chat"))

    @exception_handler
    def set_online_status(self, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.activity_status("on")
        logger.info(service_align(email, "Online status is set"))

    @exception_handler
    def change_nick_random(self, max_length, nick, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        if nick is None:
            nick = UsernameGenerator(2, max_length).generate()
        sub_client.edit_profile(nickname=nick)
        logger.info(service_align(email, f"Nickname changed to {nick}"))

    @exception_handler
    def change_icon_random(self, images: list, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        icon = client.upload_media(open(os.path.join(ICONS_PATH, f"{random.choice(images)}"), "rb"), "image")
        sub_client.edit_profile(icon=icon)
        logger.info(service_align(email, "Icon changed"))

    @exception_handler
    def wall_comment(self, userid: str, text: str, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.comment(message=text, userId=userid)
        logger.info(service_align(email, "Comment sent"))

    @exception_handler
    def vote_poll(self, blog_id: str, option_id: str, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.vote_poll(blogId=blog_id, optionId=option_id)
        logger.info(service_align(email, "Voted"))
