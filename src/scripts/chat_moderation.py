import os
import time
import traceback
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from src.utils.chat import get_chat_id
from src.utils.logger import exception_handler, logger, file_logger
from src.utils.configs import CHAT_SETTINGS_PATH, CHAT_MODERATION_MENU
from src.utils.table import create_table


class ChatModeration:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client
        while True:
            try:
                logger.info(colored(create_table("Chat Moderation", CHAT_MODERATION_MENU), "cyan"))
                choice = input("Select action >>> ")
                if choice == "1":
                    self.clear_chat(get_chat_id(self.sub_client))
                if choice == "2":
                    self.save_chat_settings(get_chat_id(self.sub_client))
                if choice == "3":
                    self.set_view_mode(get_chat_id(self.sub_client))
                if choice == "4":
                    self.set_view_mode_timer(get_chat_id(self.sub_client))
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    @exception_handler
    def clear_chat(self, chatid: str):
        count = int(input("Number of messages: "))
        pool = ThreadPool(50)
        deleted = 0
        next_page = None
        back = False
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId not in admins:
            logger.error("You don't have co-host/host rights to use this function")
            return
        while not back:
            messages = self.sub_client.get_chat_messages(chatId=chatid, size=100, pageToken=next_page)
            if not messages.messageId:
                break
            next_page = messages.nextPageToken
            for message_id in messages.messageId:
                if deleted >= count:
                    back = True
                    break
                pool.apply_async(self.sub_client.delete_message, [chatid, message_id, False, None])
                deleted += 1
                logger.info(f"{deleted} messages deleted")

    @exception_handler
    def save_chat_settings(self, chatid: str):
        if not os.path.exists(CHAT_SETTINGS_PATH):
            os.mkdir(CHAT_SETTINGS_PATH)
        with open(os.path.join(CHAT_SETTINGS_PATH, f"{chatid}.txt"), "w", encoding="utf-8") as settings_file:
            chat = self.sub_client.get_chat_thread(chatId=chatid)
            data = "====================Title====================\n" \
                   f"{chat.title}\n\n" \
                   "===================Content===================\n" \
                   f"{chat.content}\n\n" \
                   "====================Icon====================\n" \
                   f"{chat.icon}\n\n" \
                   "=================Background=================\n" \
                   f"{chat.backgroundImage}\n\n"
            if chat.announcement:
                data += "================Announcement================\n"
                data += f"{chat.announcement}\n"
            if chat.userAddedTopicList:
                data += "================Tags================\n"
                for i in chat.userAddedTopicList:
                    data += f"{i.get('name')}\nColor: {i.get('style').get('backgroundColor')}\n"
            settings_file.write(data)
        logger.info(f"Settings saved in {os.path.join(CHAT_SETTINGS_PATH, f'{chatid}.txt')}")

    @exception_handler
    def set_view_mode(self, chatid: str):
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            logger.info("Chat mode is set to logo")
        else:
            logger.error("You don't have co-host/host rights to use this function")

    @exception_handler
    def set_view_mode_timer(self, chatid: str):
        duration = int(input("Duration in seconds: "))
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            logger.info("Chat mode is set to logo")
            while duration > 0:
                logger.info(f"{duration} seconds left")
                duration -= 1
                time.sleep(1)
            self.sub_client.edit_chat(chatId=chatid, viewOnly=False)
            logger.info("View mode disabled")
        else:
            logger.error("You don't have co-host/host rights to use this function")
