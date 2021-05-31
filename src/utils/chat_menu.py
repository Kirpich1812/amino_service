import amino
from src.utils.logger import logger


def get_chat_id(sub_client: amino.SubClient):
    logger.info("1 - Select a chat from the list")
    logger.info("2 - Select chat by link")
    choice = int(input(">>> "))
    if choice == 1:
        chats = sub_client.get_chat_threads(start=0, size=100)
        for x, title in enumerate(chats.title, 1):
            logger.info(f"{x}. {title}")
        index = input("Select chat: ")
        if int(index) <= 0 or int(index) > len(chats.chatId):
            raise Exception("Invalid chat number")
        return chats.chatId[int(choice)-1]
    if choice == 2:
        link = input("Link: ")
        return sub_client.client.get_from_code(link.split("/")[-1]).objectId
