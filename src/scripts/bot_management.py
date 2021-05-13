import os
import random

import amino
from src.login import login_sid
from src.nick_gen import UsernameGenerator
from src.logger import service_log


class BotManagement:
    def __init__(self, sub_client: amino.SubClient):
        self.com_id = sub_client.comId

    def play_lottery(self, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            play = sub_client.lottery()
            award = play.awardValue if play.awardValue else 0
            service_log(email, f"+{award} coins won")
            return int(award)
        except amino.exceptions.AlreadyPlayedLottery:
            service_log(email, "AlreadyPlayedLottery")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def send_coins(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            coins = int(client.get_wallet_info().totalCoins)
            if coins != 0:
                sub_client.send_coins(coins=coins, blogId=object_id)
                service_log(email, f"+{coins} coins")
                return coins
            else:
                service_log(email, "NotEnoughCoins")
        except amino.exceptions.NotEnoughCoins:
            service_log(email, "NotEnoughCoins")
        except amino.exceptions.InvalidRequest:
            service_log(email, "InvalidRequest")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def like_blog(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.like_blog(blogId=object_id)
            service_log(email, "Like")
        except amino.exceptions.RequestedNoLongerExists:
            sub_client.like_blog(wikiId=object_id)
            service_log(email, "Like")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def join_bots_to_chat(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.join_chat(chatId=object_id)
            service_log(email, "Join")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.RemovedFromChat:
            service_log(email, "You are removed from this chatroom")
        except Exception as e:
            service_log(email, str(e))

    def leave_bots_from_chat(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.leave_chat(chatId=object_id)
            service_log(email, "Leave")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.RemovedFromChat:
            service_log(email, "You are removed from this chatroom")
        except Exception as e:
            service_log(email, str(e))

    def join_bots_to_community(self, inv_link=None, account: dict = None):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        invitation_id = None
        if inv_link:
            invitation_id = client.link_identify(code=str(inv_link.split("/")[-1])).get("invitationId")
        if invitation_id:
            try:
                client.join_community(comId=self.com_id, invitationId=invitation_id)
                service_log(email, "Join")
            except Exception as e:
                service_log(email, str(e))
        if invitation_id is None:
            client.join_community(comId=self.com_id)
            service_log(email, "Join")

    def send_message(self, object_id, text, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.send_message(chatId=object_id, message=text)
            service_log(email, "Send")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.RemovedFromChat:
            service_log(email, "You are removed from this chatroom")
        except amino.exceptions.ChatViewOnly:
            service_log(email, "Chat in view only mode")
        except amino.exceptions.AccessDenied:
            service_log(email, "Access denied")
        except Exception as e:
            service_log(email, str(e))

    def follow(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.follow(userId=object_id)
            service_log(email, "Follow")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.AccessDenied:
            service_log(email, "Access denied")
        except Exception as e:
            service_log(email, str(e))

    def unfollow(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.unfollow(userId=object_id)
            service_log(email, "Unfollow")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.AccessDenied:
            service_log(email, "Access denied")
        except Exception as e:
            service_log(email, str(e))

    def start_chat(self, object_id, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.start_chat(userId=object_id, message="")
            service_log(email, "Started chat")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except amino.exceptions.AccessDenied:
            service_log(email, "Access denied")
        except Exception as e:
            service_log(email, str(e))

    def set_online_status(self, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.activity_status("on")
            service_log(email, "Online status is set")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def change_nick_random(self, max_length, nick, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            if nick is None:
                nick = UsernameGenerator(2, max_length).generate()
            sub_client.edit_profile(nickname=nick)
            service_log(email, f"Nickname changed to {nick}")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def change_icon_random(self, images: list, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            icon = client.upload_media(open(os.path.join(os.getcwd(), "src", "icons", f"{random.choice(images)}"), "rb"), "image")
            sub_client.edit_profile(icon=icon)
            service_log(email, "Icon changed")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def wall_comment(self, userid: str, text: str, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.comment(message=text, userId=userid)
            service_log(email, "Comment sent")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))

    def vote_poll(self, blog_id: str, option_id: str, account: dict):
        email = account.get("email")
        client = login_sid(account)
        if not client:
            return
        sub_client = amino.SubClient(comId=self.com_id, client=client)
        try:
            sub_client.vote_poll(blogId=blog_id, optionId=option_id)
            service_log(email, "Voted")
        except amino.exceptions.YouAreBanned:
            service_log(email, "You are banned")
        except Exception as e:
            service_log(email, str(e))
