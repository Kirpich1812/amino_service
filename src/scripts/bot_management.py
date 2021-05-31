import os
import random

import amino
from src.utils.login import login_sid
from src.utils.nick_gen import UsernameGenerator
from src.utils.logger import service_align, lifecycle_logger, logger
from src.utils.paths import ICONS_PATH


class BotManagement:
    def __init__(self, sub_client: amino.SubClient):
        self.com_id = sub_client.comId

    @lifecycle_logger
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

    @lifecycle_logger
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

    @lifecycle_logger
    def like_blog(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.like_blog(blogId=object_id)
        logger.info(service_align(email, "Like"))

    @lifecycle_logger
    def join_bots_to_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.join_chat(chatId=object_id)
        logger.info(service_align(email, "Join"))

    @lifecycle_logger
    def leave_bots_from_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.leave_chat(chatId=object_id)
        logger.info(service_align(email, "Leave"))

    @lifecycle_logger
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

    @lifecycle_logger
    def send_message(self, object_id, text, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.send_message(chatId=object_id, message=text)
        logger.info(service_align(email, "Send"))

    @lifecycle_logger
    def follow(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.follow(userId=object_id)
        logger.info(service_align(email, "Follow"))

    @lifecycle_logger
    def unfollow(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.unfollow(userId=object_id)
        logger.info(service_align(email, "Unfollow"))

    @lifecycle_logger
    def start_chat(self, object_id, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.start_chat(userId=object_id, message="")
        logger.info(service_align(email, "Started chat"))

    @lifecycle_logger
    def set_online_status(self, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.activity_status("on")
        logger.info(service_align(email, "Online status is set"))

    @lifecycle_logger
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

    @lifecycle_logger
    def change_icon_random(self, images: list, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        icon = client.upload_media(open(os.path.join(ICONS_PATH, f"{random.choice(images)}"), "rb"), "image")
        sub_client.edit_profile(icon=icon)
        logger.info(service_align(email, "Icon changed"))

    @lifecycle_logger
    def wall_comment(self, userid: str, text: str, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.comment(message=text, userId=userid)
        logger.info(service_align(email, "Comment sent"))

    @lifecycle_logger
    def vote_poll(self, blog_id: str, option_id: str, account: tuple):
        email = account[0]
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        sub_client.vote_poll(blogId=blog_id, optionId=option_id)
        logger.info(service_align(email, "Voted"))
