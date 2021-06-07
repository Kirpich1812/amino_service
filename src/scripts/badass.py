import traceback
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from src.utils.chat import get_chat_id
from src.utils.configs import BADASS_MENU
from src.utils.logger import exception_handler, logger, file_logger
from src.utils.table import create_table


class Badass:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client
        while True:
            try:
                logger.info(colored(create_table("Badass", BADASS_MENU), "cyan"))
                choice = input("Select action >>> ")
                if choice == "1":
                    self.send_system_message(get_chat_id(self.sub_client))
                if choice == "2":
                    self.spam_system_message(get_chat_id(self.sub_client))
                if choice == "3":
                    self.delete_chat(get_chat_id(self.sub_client))
                if choice == "4":
                    self.invite_all_users(get_chat_id(self.sub_client))
                if choice == "5":
                    self.spam_posts()
                if choice == "6":
                    self.spam_public_chats()
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    @exception_handler
    def send_system_message(self, chatid: str):
        self.sub_client.join_chat(chatid)
        while True:
            message_type = int(input("Message type: "))
            message = input("Message text: ")
            self.sub_client.send_message(chatId=chatid, messageType=message_type, message=message)
            logger.info("Message sent")
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break

    @exception_handler
    def spam_system_message(self, chatid: str):
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        message = input("Message text: ")
        message_type = int(input("Message type: "))
        self.sub_client.join_chat(chatid)
        logger.info("Spam has been started...")
        while True:
            tasks = [pool.apply_async(self.sub_client.send_message, [message, message_type, chatid]) for _ in range(pool_count)]
            for x in tasks:
                x.get()

    @exception_handler
    def delete_chat(self, chatid: str):
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.kick(chatId=chatid, allowRejoin=False, userId=chat.author.userId)
            logger.info("Chat deleted")
        else:
            logger.error("You don't have co-host/host rights to use this function")

    @exception_handler
    def invite_all_users(self, chatid: str):
        pool = ThreadPool(100)
        count = 0
        for i in range(0, 10000, 100):
            users = self.sub_client.get_online_users(start=i, size=100).profile.userId
            if not users:
                break
            for userid in users:
                pool.apply_async(self.sub_client.invite_to_chat, [userid, chatid])
                count += 1
                logger.info(f"{count} users invited to chat")
        logger.info("All online users invited to chat")

    @exception_handler
    def spam_posts(self):
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        posts_count = int(input("Count of posts: "))
        title = input("Post title: ")
        content = input("Post content: ")
        while True:
            for i in range(posts_count):
                logger.info("Post sent")
                pool.apply_async(self.sub_client.post_blog, [title, content])
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break

    @exception_handler
    def spam_public_chats(self):
        message = input("Message: ")
        message_type = int(input("Message type: "))
        logger.info("Spam has been started...")
        pool = ThreadPool(100)
        for i in range(0, 5000, 100):
            chats = self.sub_client.get_public_chat_threads(start=i, size=100).chatId
            if not chats:
                break
            tasks = [pool.apply_async(self.sub_client.join_chat, [x]) for x in chats]
            for x in tasks:
                try: x.get()
                except: pass
            tasks = [pool.apply_async(self.sub_client.send_message, [message, message_type, x]) for x in chats]
            for x in tasks:
                try: x.get()
                except: pass
