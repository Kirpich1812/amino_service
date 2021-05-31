import os
import random

import amino
from src.utils.logger import lifecycle_logger, logger
from src.utils.nick_gen import UsernameGenerator
from src.utils.paths import ACCOUNTS_DIR_PATH, REG_DEVICES_PATH, CREATED_ACCOUNTS_PATH, DEVICE_IDS_PATH

device_id_list = open(DEVICE_IDS_PATH, "r").readlines()


class CreateAccounts:
    def __init__(self):
        self.client = amino.Client()
        self.email = None
        self.password = input("Set a password for all accounts: ")
        while len(self.password) < 6:
            logger.error("Password must be at least 6 characters long")
            self.password = input("Set a password for all accounts: ")
        self.code = None
        self.count = 0

    @lifecycle_logger
    def run(self):
        if not os.path.exists(ACCOUNTS_DIR_PATH):
            os.mkdir(ACCOUNTS_DIR_PATH)
        if not os.path.exists(REG_DEVICES_PATH):
            logger.error(REG_DEVICES_PATH + " not found")
            return
        reg_devices = open(REG_DEVICES_PATH, "r").readlines()
        if reg_devices:
            for device in reg_devices:
                self.client.device_id = self.client.headers.device_id = device.replace("\n", "")
                for _ in range(3):
                    self.email = input("Email: ")
                    if self.register():
                        self.client.request_verify_code(email=self.email)
                        if self.verify():
                            if self.login():
                                if self.activate():
                                    self.save_account()
                                    self.count += 1
                                    logger.info(f"{self.count} accounts registered")
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                self.remove_device()
        else:
            logger.error("reg_devices.txt is empty")

    def register(self):
        while True:
            try:
                nick = UsernameGenerator(2, 10).generate()
                self.client.register(nickname=nick, email=self.email, password=str(self.password))
                return True
            except amino.exceptions.VerificationRequired as e:
                input("Open this link in a browser and click the checkmark: " + e.args[0]["url"] + "\n\npress ENTER to continue...")
            except Exception as e:
                logger.error(e.args[0]["api:message"])
                return False

    def verify(self):
        while True:
            self.code = input("Code: ")
            try:
                self.client.verify(email=self.email, code=self.code)
                return True
            except Exception as e:
                logger.error(e.args[0]["api:message"])
                return False

    def login(self):
        while True:
            try:
                self.client.login(email=self.email, password=self.password)
                return True
            except amino.exceptions.ActionNotAllowed:
                self.client.device_id = self.client.headers.device_id = random.choice(device_id_list).replace("\n", "")
            except Exception as e:
                logger.error(e.args[0]["api:message"])
                return False

    def activate(self):
        while True:
            try:
                self.client.activate_account(email=self.email, code=self.code)
                return True
            except Exception as e:
                logger.error(e.args[0]["api:message"])
                return False

    def save_account(self):
        with open(CREATED_ACCOUNTS_PATH, "a") as accounts_file:
            accounts_file.write(f"{self.email}:{self.password}\n")
        logger.info(f"{self.email} saved in " + CREATED_ACCOUNTS_PATH)

    def remove_device(self):
        devices = open(REG_DEVICES_PATH, "r").readlines()
        devices.pop(0)
        with open(REG_DEVICES_PATH, "w") as devices_file:
            for i in devices:
                devices_file.write(i)
