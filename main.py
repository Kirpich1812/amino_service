import json
import os
import traceback
from sys import platform

import requests
from colorama import init
from termcolor import colored

from src.utils.logger import logger, file_logger
from src.utils.configs import LOGO_VIEW_PATH
from src.service import ServiceApp

if __name__ == '__main__':
    if platform != "linux":
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW("Amino Service")
    os.system('cls' if os.name == 'nt' else 'clear')
    init()

    __info__ = json.loads(requests.get("https://github.com/LynxN1/amino_service/raw/master/version.json").text)

    __version__   = __info__["version"]
    __author__    = __info__["author"]
    __github__    = __info__["github"]
    __telegram__  = __info__["telegram"]
    try:
        __current__ = json.loads(open("version.json").read())["version"]
    except:
        __current__ = None

    if __version__ != __current__:
        logger.warning(f"New version of Amino Service available! ({__version__})\n")

    logger.info(colored(open(LOGO_VIEW_PATH, "r").read().replace("_", " "), "green"))
    logger.info(colored(f"Author     {__author__}\n"
                        f"Version    {__current__}\n"
                        f"Github     {__github__}\n"
                        f"Telegram   {__telegram__}\n", "green"))

    try:
        ServiceApp().run()
    except Exception as e:
        logger.error(e)
        file_logger.debug(traceback.format_exc())
