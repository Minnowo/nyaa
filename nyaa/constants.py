

########################################################################
####################### main config for functionality ##################
########################################################################
BOT_CONFIG            = "config\\bot.json"                             # bot information 
CONFIG_FILE           = "config\\conf.json"                            # currently does nothing
LEAVE_JOIN_CONFIG     = "config\\leave_join.json"                      # contains data for leave/join cog
REACTION_ROLES_CONFIG = "config\\reaction_roles.json"                  # contains data for reaction roles
RSS_CONFIG            = "config\\rss.json"                             # contains data for rss feed 
########################################################################
####################### sauce command url files ########################
########################################################################

CONFIG_FORMAT = "config\\sauce\\{0}\\{0}_line.txt"
LINKS_FORMAT = "config\\sauce\\{0}\\{0}_links.txt"

SAUCE_MAP = {
    "thighs" : {
        "config" : CONFIG_FORMAT.format("thighs"),
        "links" : LINKS_FORMAT.format("thighs")
    },
    "feet" : {
        "config" :  CONFIG_FORMAT.format("feet"),
        "links" : LINKS_FORMAT.format("feet")
    },
    "cutegirls" : {
        "config" : CONFIG_FORMAT.format("cutegirls"),
        "links" : LINKS_FORMAT.format("cutegirls")
    },
    "kemonomimi" : {
        "config" : CONFIG_FORMAT.format("kemonomimi"),
        "links" : LINKS_FORMAT.format("kemonomimi")
    },
    "appleworm" : {
        "config" : CONFIG_FORMAT.format("appleworm"),
        "links" : LINKS_FORMAT.format("appleworm")
    },
    "gura" : {
        "config" : CONFIG_FORMAT.format("gura"),
        "links" : LINKS_FORMAT.format("gura")
    },
    "femboy" : {
        "config" : CONFIG_FORMAT.format("femboy"),
        "links" : LINKS_FORMAT.format("femboy")
    },
    "bondage" : {
        "config" : CONFIG_FORMAT.format("bondage"),
        "links" : LINKS_FORMAT.format("bondage")
    },
    "witch" : {
        "config" : CONFIG_FORMAT.format("witch"),
        "links" : LINKS_FORMAT.format("witch")
    },
    "hutao" : {
        "config" : CONFIG_FORMAT.format("hutao"),
        "links" : LINKS_FORMAT.format("hutao")
    },
    "rushia" : {
        "config" : CONFIG_FORMAT.format("rushia"),
        "links" : LINKS_FORMAT.format("rushia")
    },
    "fubuki" : {
        "config" : CONFIG_FORMAT.format("fubuki"),
        "links" : LINKS_FORMAT.format("fubuki")
    },
    "okayu" : {
        "config" : CONFIG_FORMAT.format("okayu"),
        "links" : LINKS_FORMAT.format("okayu")
    },
    "pekora" : {
        "config" : CONFIG_FORMAT.format("pekora"),
        "links" : LINKS_FORMAT.format("pekora")
    },
    "mori" : {
        "config" : CONFIG_FORMAT.format("mori"),
        "links" : LINKS_FORMAT.format("mori")
    },
    "suisei" : {
        "config" : CONFIG_FORMAT.format("suisei"),
        "links" : LINKS_FORMAT.format("suisei")
    },
    "navel" : {
        "config" : CONFIG_FORMAT.format("navel"),
        "links" : LINKS_FORMAT.format("navel")
    },
    "panties" : {
        "config" : CONFIG_FORMAT.format("panties"),
        "links" : LINKS_FORMAT.format("panties")
    }
}

########################################################################
####################### exe / external runs ############################
########################################################################
FFMPEG = "ffmpeg.exe"                                                  # path to ffmpeg for music commands 
########################################################################
######################## downloada directories #########################
########################################################################
DL_MUSIC   = "dls\\music\\"                                            # download path for music
DL_NHENTAI = "dls\\nhentai\\"                                          # download path for nhentai
########################################################################
########################### colors #####################################
########################################################################
EMBED_COLOR = 0xBCD0F7                                                 # default embed color
EMBED_USER_LEFT_COLOR = 0xED152E                                       # color used for user leave embed
EMBED_USER_JOIN_COLOR = 0x04c41a                                       # color used for user joined embed 
########################################################################
############################# other ####################################
########################################################################
VALID_AUDIO_FILES = ['mp3','wav','flac','aac','ogg']                   # file extension that can be downloaded for the music bot 
# event names 
MEMBER_JOIN  = "join"
MEMBER_LEAVE = "leave"
REACTION_CHANGED = "reaction_changed"
MESSAGE_DELETED  = "message_deleted"

JOKE_HELP = ["uwu", "owo", "*prrrr*", "nyaa~ ;3c", "*teehee*", "*prrrr*"]

if __name__ == "__main__":
    import os 

    os.makedirs(DL_MUSIC, exist_ok=True)
    os.makedirs(DL_NHENTAI, exist_ok=True)

    for i in SAUCE_MAP:
        print(i)
        
        os.makedirs(os.path.dirname(CONFIG_FORMAT.format(i)), exist_ok=True)

        if not os.path.isfile(SAUCE_MAP[i]["config"]):
            with open(SAUCE_MAP[i]["config"], "w") as writer:
                writer.write("")

        if not os.path.isfile(SAUCE_MAP[i]["links"]):
            with open(SAUCE_MAP[i]["links"], "w") as writer:
                writer.write("")
