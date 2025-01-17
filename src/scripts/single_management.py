import random
import traceback
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from src.utils.configs import MAIN_ACCOUNT_MENU
from src.utils.logger import exception_handler, logger, file_logger
from src.utils.table import create_table


class SingleManagement:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client
        while True:
            try:
                logger.info(colored(create_table("Main Account", MAIN_ACCOUNT_MENU), "cyan"))
                choice = input("Select action >>> ")
                if choice == "1":
                    quiz_link = input("Quiz link: ")
                    object_id = self.sub_client.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                    self.play_quiz(object_id)
                if choice == "2":
                    self.like_recent_blogs()
                if choice == "3":
                    self.follow_all()
                if choice == "4":
                    self.unfollow_all()
                if choice == "5":
                    self.get_blocker_users()
                if choice == "6":
                    coins_count = input("Number of coins: ")
                    blog_link = input("Blog link: ")
                    object_id = self.sub_client.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    self.send_coins(int(coins_count), object_id)
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    @exception_handler
    def play_quiz(self, object_id: str):
        questions_list = []
        answers_list = []

        quiz_info = self.sub_client.get_blog_info(quizId=object_id).json
        questions = quiz_info["blog"]["quizQuestionList"]
        total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

        for x, question in enumerate(questions, 1):
            logger.info(f"[{x}/{total_questions}]: Choosing the right answer...")
            question_id = question["quizQuestionId"]
            answers = question["extensions"]["quizQuestionOptList"]
            for answer in answers:
                answer_id = answer["optId"]
                self.sub_client.play_quiz(quizId=object_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                latest_score = self.sub_client.get_quiz_rankings(quizId=object_id).profile.latestScore
                if latest_score > 0:
                    logger.info(f"[{x}/{total_questions}]: Answer found!")
                    questions_list.append(question_id)
                    answers_list.append(answer_id)
        for i in range(2):
            try:
                self.sub_client.play_quiz(quizId=object_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=i)
            except:
                pass
        logger.info(f"[quiz]: Passed the quiz!")
        logger.info(f"[quiz]: Score: {self.sub_client.get_quiz_rankings(quizId=object_id).profile.highestScore}")

    @exception_handler
    def unfollow_all(self):
        pool_count = int(input("Number of threads: "))
        thread_pool = ThreadPool(pool_count)
        x = 0
        count = 0
        while True:
            followings = self.sub_client.get_user_following(userId=self.sub_client.profile.userId, start=x, size=100)
            x += 100
            if not followings.userId:
                break
            for i in followings.userId:
                thread_pool.apply_async(self.sub_client.unfollow, [i])
                count += 1
                logger.info(f"Unfollowing: {count}")

    @exception_handler
    def like_recent_blogs(self):
        comments = []
        x = 0
        while True:
            x += 1
            comment = input(f"Enter your comment text (optional)[{x}]: ")
            if comment:
                comments.append(comment)
            if not comment:
                break
        count = 0
        old = []
        token = None
        for x in range(0, 100000, 100):
            blogs = self.sub_client.get_recent_blogs(pageToken=token, start=x, size=100)
            token = blogs.nextPageToken
            if token in old:
                break
            old.append(token)
            for blog_id in blogs.blogId:
                if blog_id in old:
                    continue
                old.append(blog_id)
                try:
                    self.sub_client.like_blog(blogId=blog_id)
                    count += 1
                    logger.info(f"{count} posts liked")
                    self.sub_client.comment(blogId=blog_id, message=random.choice(comments))
                except:
                    pass

    @exception_handler
    def follow_all(self):
        old = []
        pool = ThreadPool(100)
        count = 0
        for i in range(0, 20000, 100):
            recent_users = self.sub_client.get_all_users(type="recent", start=i, size=100).profile.userId
            users = [*recent_users]
            if not users:
                break
            for _ in range(2):
                pool.apply_async(self.sub_client.follow, [users])
            count += len(users)
            logger.info(f"Follow to {count} users")
        for i in range(0, 20000, 100):
            online_users = self.sub_client.get_online_users(start=i, size=100).profile.userId
            users = [*online_users]
            if not users:
                break
            for _ in range(2):
                pool.apply_async(self.sub_client.follow, [users])
            count += len(users)
            logger.info(f"Follow to {count} users")
        for i in range(0, 20000, 100):
            banned_users = self.sub_client.get_all_users(type="banned", start=i, size=100).profile.userId
            users = [*banned_users]
            if not users:
                break
            for _ in range(2):
                pool.apply_async(self.sub_client.follow, [users])
            count += len(users)
            logger.info(f"Follow to {count} users")
        for i in range(0, 20000, 100):
            chats = self.sub_client.get_public_chat_threads(type="recommended", start=i, size=100).chatId
            if not chats:
                break
            for chatid in chats:
                for x in range(0, 1000, 100):
                    users = self.sub_client.get_chat_users(chatId=chatid, start=x, size=100).userId
                    if not users:
                        break
                    for userid in old:
                        if userid in users:
                            users.remove(userid)
                    for _ in range(2):
                        pool.apply_async(self.sub_client.follow, [users])
                    count += len(users)
                    logger.info(f"Follow to {count} users")

    @exception_handler
    def get_blocker_users(self):
        users = self.sub_client.get_blocker_users(start=0, size=100)
        if not users:
            return
        for i in users:
            user = self.sub_client.get_user_info(i)
            logger.info(f"Userid: {i}")
            logger.info(f"Nickname: {user.nickname}")
            logger.info("")

    @exception_handler
    def send_coins(self, count: int, blog_id: str):
        pool = ThreadPool(3)
        if count <= 500:
            self.sub_client.send_coins(coins=count, blogId=blog_id)
            logger.info(f"Sent {count} coins")
        else:
            ready = 0
            for _ in range(int(count / 500)):
                pool.apply_async(self.sub_client.send_coins, [500, blog_id])
                ready += 500
                logger.info(f"Sent {ready} coins")
            if count % 500 >= 1:
                self.sub_client.send_coins(coins=count % 500, blogId=blog_id)
                ready += count % 500
                logger.info(f"Sent {ready} coins")
