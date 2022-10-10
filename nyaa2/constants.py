import os 
import logging

BASE = ".\\"
CONFIG_DIR = f"{BASE}.nyaa\\" 
CONFIG_DB_DIR = f"{CONFIG_DIR}db\\" 
CONFIG_JSON_DIR = f"{CONFIG_DIR}json\\" 
CONFIG_LOGS_DIR = f"{CONFIG_DIR}logs\\" 

DIRECTORIES = [ BASE, CONFIG_DIR, CONFIG_DB_DIR, CONFIG_JSON_DIR, CONFIG_LOGS_DIR ]

BOT_CONFIG            = f"{CONFIG_JSON_DIR}bot.json"                             # bot information 
LEAVE_JOIN_CONFIG     = f"{CONFIG_JSON_DIR}leave_join.json"                      # contains data for leave/join cog
REACTION_ROLES_CONFIG = f"{CONFIG_JSON_DIR}reaction_roles.json"                  # contains data for reaction roles
RSS_CONFIG            = f"{CONFIG_JSON_DIR}rss.json"                             # contains data for rss feed 

DATABASE_PATH         = f"{CONFIG_DB_DIR}main.db"
DATABASE_IMAGES_PATH  = f"{CONFIG_DB_DIR}images.db"
DATABASE_LOG_PATH     = f"{CONFIG_DB_DIR}logs.db"

NYAA2_BASE_LOGGER     = ("[Main] Nyaa2 Base", f"{CONFIG_LOGS_DIR}Nyaa2.log", logging.INFO)
COG_BASE_LOGGER       = ("[Cog] Base", f"{CONFIG_LOGS_DIR}CogBaseLogger.log", logging.INFO)
COG_BOT_EVENTS_LOGGER = ("[Cog] Bot Events", f"{CONFIG_LOGS_DIR}CogBotEvents.log", logging.INFO)
COG_SERVER_UTIL_LOGGER = ("[Cog] Server Util", f"{CONFIG_LOGS_DIR}CogServerUtil.log", logging.INFO)
IMAGE_COMMANDS_LOGGER = ("[Cog] Image Commands", f"{CONFIG_LOGS_DIR}CogImageCommands.log", logging.INFO)
DB_BASE_LOGGER = ("[DB] Image Commands", f"{CONFIG_LOGS_DIR}DbBaseLogger.log", logging.INFO)

EMBED_COLOR = 0xBCD0F7                                                 # default embed color
EMBED_USER_LEFT_COLOR = 0xED152E                                       # color used for user leave embed
EMBED_USER_JOIN_COLOR = 0x04c41a                                       # color used for user joined embed 

# event names 
MEMBER_JOIN  = "join"
MEMBER_LEAVE = "leave"
REACTION_CHANGED = "reaction_changed"
MESSAGE_DELETED  = "message_deleted"


WINDOWS = (os.name == "nt")


from re import compile 

# used for getting the channel id from a mention -> <#insert channel id here>
PARSE_CHANNEL_MENTION = compile(r"\<\#(\d+)\>")
PARSE_USER_MENTION    = compile(r"\<\@(\d+)\>")
PARSE_ROLE_MENTION    = compile(r"\<\@\&(\d+)\>")

MATCH_RE_DISCORD_LINK = compile(r"(?:https?://)(?:(?:cdn\.discordapp\.com)|(?:media\.discordapp\.net))/attachments/\d+/\d+/[^\s]+")



from argparse import Namespace

bcolors = Namespace(
    HEADER="\033[95m",
    OKBLUE="\033[94m",
    OKCYAN="\033[96m",
    OKGREEN="\033[92m",
    WARNING="\033[93m",
    FAIL="\033[91m",     # red error color
    ENDC="\033[0m",
    BOLD="\033[1m",
    UNDERLINE="\033[4m",
)



IMAGE_CACHE_SIZE = 25

HELP_MESSAGE = "actual help message coming soon"


IMAGE_CATEGORY_MAP = {
    'astolfo': 1, 
    'appleworm': 2, 'bondage': 3, 'cutegirls': 4, 'feet': 5, 'femboy': 6, 'fubuki': 7,
    'gura': 8, 'hutao': 9, 'kemonomimi': 10, 'mori': 11, 'navel': 12,
    'okayu': 13, 'panties': 14, 'pekora': 15, 'rushia': 16, 'suisei': 17, 
    'thighs': 18, 'witch': 19, 'nyaa': 20, 'ranni': 21, 
    'laplus': 22, 'subaru': 23, 
    'baelz': 24}

JOKE_HELP = ["uwu", "owo", "*prrrr*", "nyaa~ ;3c", "*teehee*", "*prrrr*", HELP_MESSAGE]