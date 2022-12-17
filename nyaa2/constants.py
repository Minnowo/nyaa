import os 
import logging

BASE = ".\\"
CONFIG_DIR = f"{BASE}.nyaa\\" 
CONFIG_DB_DIR = f"{CONFIG_DIR}db\\" 
CONFIG_JSON_DIR = f"{CONFIG_DIR}json\\" 
CONFIG_LOGS_DIR = f"{CONFIG_DIR}logs\\" 

DIRECTORIES = [ BASE, CONFIG_DIR, CONFIG_DB_DIR, CONFIG_JSON_DIR, CONFIG_LOGS_DIR ]

BOT_CONFIG            = f"{CONFIG_JSON_DIR}bot.json"                             # bot information 

DATABASE_PATH         = f"{CONFIG_DB_DIR}main.db"
DATABASE_IMAGES_PATH  = f"{CONFIG_DB_DIR}images.db"
DATABASE_LOG_PATH     = f"{CONFIG_DB_DIR}logs.db"
DATABASE_MISC_PATH    = f"{CONFIG_DB_DIR}misc.db"

NYAA2_BASE_LOGGER      = ("[Main] Nyaa2 Base", f"{CONFIG_LOGS_DIR}Nyaa2.log", logging.INFO)
COG_BASE_LOGGER        = ("[Cog] Base", f"{CONFIG_LOGS_DIR}CogBaseLogger.log", logging.INFO)
DB_BASE_LOGGER         = ("[DB] Image Commands", f"{CONFIG_LOGS_DIR}DbBaseLogger.log", logging.INFO)

URL_SAVE = f"{CONFIG_DIR}links.txt"

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
IS_ONLY_A_TO_Z        = compile(r"^[a-zA-Z_]+$")
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


SIZE_SUFFIXES = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

IMAGE_CACHE_SIZE = 25

HELP_MESSAGE = """```
--~ Nyaa2 Help ~--

I can't believe you actually got the help message :flushed:

Aliases to commands will be put in [] and arguments in () and ? for optional arguments

--~ Server Util ~-- 

- getuser   (ID/Mention) [getmember] [user] [member] [fetchuser]
- clear     (?MsgCount)  [delete] [purge]
- random    (Min) (Max)  [rand] [rnd] [rng]
- invite                 [getinvite]
- getserver (?ServerID)  [server] [fetchserver] [guild] [getguild]

- leave_join_message        ('leave'/'join') [ljm]
- remove_leave_join_message ('leave'/'join') [rljm]


--~ Images ~-- 

sfw channels get sfw images and 18+ channels get nsfw (hopefully)

If you get a "Could not find image" response, there is most likely no sfw/nsfw images 

- astolfo    (?sfw/nsfw)
- appleworm  (?sfw/nsfw) [worm]
- bondage    (?sfw/nsfw) [bdsm]
- cutegirls  (?sfw/nsfw) [girl]
- feet       (?sfw/nsfw)
- femboy     (?sfw/nsfw) [trap]
- fubuki     (?sfw/nsfw)
- gura       (?sfw/nsfw)
- hutao      (?sfw/nsfw)
- kemonomimi (?sfw/nsfw) [kemo] [neko]
- mori       (?sfw/nsfw) [cali]
- navel      (?sfw/nsfw) [stomach]
- okayu      (?sfw/nsfw)
- panties    (?sfw/nsfw) [pantsu]
- pekora     (?sfw/nsfw) [peko]
- rushia     (?sfw/nsfw)
- suisei     (?sfw/nsfw) [sui]
- thighs     (?sfw/nsfw) [thigh]
- witch      (?sfw/nsfw)
- nyaa       (?sfw/nsfw) [nya] [nyaaa]...
- ranni      (?sfw/nsfw)
- laplus     (?sfw/nsfw) [la+]
- subaru     (?sfw/nsfw) 
- baelz      (?sfw/nsfw) [hakos] [hakosbaelz] [bae]
- towa       (?sfw/nsfw)

- imid (id) [imbyid]

--~ Trusted ~--

Commands for trusted users 

- setr    (ImgID) (Rating)
- trust   (ID/Mention)
- untrust (ID/Mention)
- listc                  [listcat] [listcategory]
- addcat (Category Name) [add_category] [addcategory]
- add    (Category Name) (sfw/nsfw) (then attach images to add) [add_image] [addimage]


```"""


IMAGE_CATEGORY_MAP = {}

JOKE_HELP = ["uwu", "owo", "*prrrr*", "nyaa~ ;3c", "*teehee*", "*prrrr*", HELP_MESSAGE]
