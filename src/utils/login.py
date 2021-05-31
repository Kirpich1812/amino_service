import random
import time
import traceback
from multiprocessing.pool import ThreadPool

import amino
from src.utils.database import DatabaseController
from src.utils.logger import service_align, logger, file_logger
from src.utils.paths import DEVICE_IDS_PATH

device_id_list = open(DEVICE_IDS_PATH, "r").readlines()


def login(account: tuple):
    client = amino.Client()
    email = account[0]
    password = account[1]
    while True:
        try:
            client.login(email, password)
            return client
        except amino.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(device_id_list).replace("\n", "")
        except amino.exceptions.VerificationRequired as verify:
            logger.error("[" + email + "]: " + str(verify.args[0]["url"]))
            return False
        except Exception as e:
            logger.error("[" + email + "]: " + e.args[0]["api:message"])
            file_logger.debug(traceback.format_exc())
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
                client.device_id = client.headers.device_id = random.choice(device_id_list).replace("\n", "")
            except amino.exceptions.VerificationRequired as verify:
                logger.error(service_align(email, verify.args[0]["url"]))
                return False
            except Exception as e:
                logger.error(service_align(email, e.args[0]["api:message"]))
                file_logger.debug(traceback.format_exc())
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
        logger.warning(f"{len(invalids)} invalid accounts")
    if bads:
        logger.warning(f"{len(bads)} accounts require a SID update, start updating...")
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
