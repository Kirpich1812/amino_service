import random
import time
import traceback
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from src.database import DatabaseController
from src.logger import service_log, logger


def login(account: tuple):
    client = amino.Client()
    email = account[0]
    password = account[1]
    while True:
        try:
            client.login(email, password)
            return client
        except amino.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(DatabaseController().get_device_ids())[0]
        except amino.exceptions.FailedLogin:
            service_log(email, "Failed login")
            return False
        except amino.exceptions.InvalidAccountOrPassword:
            service_log(email, "Invalid account or password")
            return False
        except amino.exceptions.InvalidPassword:
            service_log(email, "Invalid Password")
            return False
        except amino.exceptions.InvalidEmail:
            service_log(email, "Invalid Email")
            return False
        except amino.exceptions.AccountDoesntExist:
            service_log(email, "Account does not exist")
            return False
        except amino.exceptions.VerificationRequired as verify:
            service_log(email, str(verify))
            return False
        except Exception as e:
            service_log(email, str(e))
            logger.debug(traceback.format_exc())
            return False


def login_sid(account: tuple):
    client = amino.Client()
    email = account[0]
    sid = account[2]
    is_valid = account[3]
    if is_valid == 1:
        while True:
            try:
                client.login_sid(sid)
                return client
            except amino.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(DatabaseController().get_device_ids())[0]
            except amino.exceptions.FailedLogin:
                service_log(email, "Failed login")
                return False
            except amino.exceptions.InvalidAccountOrPassword:
                service_log(email, "Invalid account or password")
                return False
            except amino.exceptions.InvalidPassword:
                service_log(email, "Invalid Password")
                return False
            except amino.exceptions.InvalidEmail:
                service_log(email, "Invalid Email")
                return False
            except amino.exceptions.AccountDoesntExist:
                service_log(email, "Account does not exist")
                return False
            except amino.exceptions.VerificationRequired as verify:
                service_log(email, str(verify))
                return False
            except Exception as e:
                service_log(email, str(e))
                logger(traceback.format_exc())
                return False


def check_accounts():
    accounts = DatabaseController().get_bots()
    invalids = []
    bads = []
    for i in accounts:
        sid = i[2]
        is_valid = i[3]
        valid_time = i[4]
        if is_valid == 0:
            invalids.append(i)
            continue
        if sid is None or valid_time is None or is_valid is None:
            bads.append(i)
            continue
        if valid_time <= int(time.time()):
            bads.append(i)
            continue
    if invalids:
        print(colored(f"{len(invalids)} invalid accounts", "red"))
    if bads:
        print(f"{len(bads)} accounts require a SID update, start updating...")
        pool = ThreadPool(50)
        valid_list = pool.map(update_sid, bads)
        for i in valid_list:
            DatabaseController().remove_bot(i.get("email"))
        DatabaseController().set_bots(valid_list)


def update_sid(account: tuple):
    email = account[0]
    password = account[1]
    client = login(account)
    if client:
        return {"email": email, "password": password, "sid": client.sid, "isValid": True, "validTime": int(time.time()) + 43200}
    else:
        return {"email": email, "password": password, "isValid": False}
