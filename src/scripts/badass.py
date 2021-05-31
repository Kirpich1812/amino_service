from functools import partial
from multiprocessing.pool import ThreadPool

import amino
from src.utils.logger import lifecycle_logger, logger


class Badass:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client

    @lifecycle_logger
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

    @lifecycle_logger
    def spam_system_message(self, chatid: str):
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        count_messages = int(input("Count of messages: "))
        message_type = int(input("Message type: "))
        message = input("Message text: ")
        self.sub_client.join_chat(chatid)
        while True:
            logger.info("Spam has been started...")
            pool.map(partial(self.sub_client.send_message, chatid, message), [message_type] * count_messages)
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break

    @lifecycle_logger
    def delete_chat(self, chatid: str):
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.kick(chatId=chatid, allowRejoin=False, userId=chat.author.userId)
            logger.info("Chat deleted")
        else:
            logger.error("You don't have co-host/host rights to use this function")

    @lifecycle_logger
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

    @lifecycle_logger
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
