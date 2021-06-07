import os

LOG_FILE_PATH               = os.path.join(os.getcwd(), "log.log")
DEVICE_IDS_PATH             = os.path.join(os.getcwd(), "src", "temp", "devices.txt")
DATABASE_PATH               = os.path.join(os.getcwd(), "src", "temp", "database.db")
LOGO_VIEW_PATH              = os.path.join(os.getcwd(), "src", "logo", "logo.txt")
ICONS_PATH                  = os.path.join(os.getcwd(), "src", "icons")
CHAT_SETTINGS_PATH          = os.path.join(os.getcwd(), "src", "chat_settings")
ACCOUNTS_DIR_PATH           = os.path.join(os.getcwd(), "src", "accounts")
REG_DEVICES_PATH            = os.path.join(os.getcwd(), "src", "accounts", "reg_devices.txt")
CREATED_ACCOUNTS_PATH       = os.path.join(os.getcwd(), "src", "accounts", "created_accounts.txt")
BOTS_TXT_PATH               = os.path.join(os.getcwd(), "src", "bots.txt")

MAIN_MENU = [
    ["0", "Add accounts from bots.txt to database"],
    ["1", "Main Account"],
    ["2", "Bots"],
    ["3", "Chat Moderation"],
    ["4", "Badass"],
    ["5", "Create accounts"]
]

MAIN_ACCOUNT_MENU = [
    ["b", "Back"],
    ["1", "Play quiz"],
    ["2", "Like + comment recent blogs"],
    ["3", "Follow all"],
    ["4", "Unfollow all"],
    ["5", "List of users who blocked you"],
    ["6", "Send coins"]
]

BOTS_MANAGEMENT_MENU = [
    ["b", "Back"],
    ["s", "Show bots list"],
    ["d", "Delete bot account from database"],
    ["1", "Play lottery"],
    ["2", "Send coins"],
    ["3", "Like blog"],
    ["4", "Join bots to chat"],
    ["5", "Remove bots from chat"],
    ["6", "Join bots to community"],
    ["7", "Send message to chat"],
    ["8", "Follow bots to user"],
    ["9", "Unfollow bots from user"],
    ["10", "Change nickname"],
    ["11", "Wall comment"],
    ["12", "Change icon"],
    ["13", "Vote for the selected option"],
    ["14", "Start chat with user"]
]

CHAT_MODERATION_MENU = [
    ["b", "Back"],
    ["1", "Clear chat messages"],
    ["2", "Save chat settings"],
    ["3", "Set logo only mode"],
    ["4", "Set logo only mode (on timer)"]
]

BADASS_MENU = [
    ["b", "Back"],
    ["1", "Send system message"],
    ["2", "Spam system messages"],
    ["3", "Delete chat(Co-Host)"],
    ["4", "Invite all online users to chat"],
    ["5", "Spam posts"],
    ["6", "Spam public chats"]
]
