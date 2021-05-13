import os
import random
import time
import traceback
from multiprocessing.pool import ThreadPool

import yaml
from termcolor import colored

import amino
from src.logger import service_log, logger
from src.other import get_accounts


def login(account: dict):
    client = amino.Client()
    email = account.get("email")
    password = account.get("password")
    while True:
        try:
            client.login(email, password)
            return client
        except amino.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(open(os.path.join(os.getcwd(), "src", "devices", "devices.txt"), "r").readlines()).replace("\n", "")
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


def login_sid(account: dict):
    client = amino.Client()
    email = account.get("email")
    sid = account.get("sid")
    is_valid = account.get("isValid")
    if is_valid:
        while True:
            try:
                client.login_sid(sid)
                return client
            except amino.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(open(os.path.join(os.getcwd(), "src", "devices", "devices.txt"), "r").readlines()).replace("\n", "")
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
    accounts = get_accounts()
    invalids = []
    bads = []
    for i in accounts:
        if i.get("isValid") is False:
            invalids.append(i)
            continue
        if i.get("sid") is None or i.get("validTime") is None or i.get("isValid") is None:
            bads.append(i)
            continue
        if i.get("validTime") <= int(time.time()):
            bads.append(i)
            continue
    if invalids:
        print(colored(f"{len(invalids)} invalid accounts", "red"))
    if bads:
        print(f"{len(bads)} accounts require a SID update, start updating...")
        pool = ThreadPool(50)
        valid_list = pool.map(update_sid, bads)
        with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as accounts_file:
            yaml.dump(valid_list, accounts_file, Dumper=yaml.Dumper)


def update_sid(account: dict):
    email = account.get("email")
    password = account.get("password")
    client = login(account)
    if client:
        return {"email": email, "password": password, "sid": client.sid, "isValid": True, "validTime": int(time.time()) + 43200}
    else:
        return {"email": email, "password": password, "isValid": False}
