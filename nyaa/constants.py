

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
THIGH_KEY      = "thighs"
THIGH_CONFIG   = "config\\{0}\\{0}_line.txt".format(THIGH_KEY)
THIGH_LINKS    = "config\\{0}\\{0}_urls.txt".format(THIGH_KEY)

FEET_KEY      = "feet"
FEET_CONFIG   = "config\\{0}\\{0}_line.txt".format(FEET_KEY)
FEET_LINKS    = "config\\{0}\\{0}_urls.txt".format(FEET_KEY)

CUTE_GIRLS_MOE_KEY    = "cutegirls"
CUTE_GIRLS_MOE_CONFIG = "config\\{0}\\{0}_line.txt".format(CUTE_GIRLS_MOE_KEY)
CUTE_GIRLS_MOE_LINKS  = "config\\{0}\\{0}_urls.txt".format(CUTE_GIRLS_MOE_KEY)

KEMONOMIMI_KEY    = "kemonomimi"
KEMONOMIMI_CONFIG = "config\\{0}\\{0}_line.txt".format(KEMONOMIMI_KEY)
KEMONOMIMI_LINKS  = "config\\{0}\\{0}_urls.txt".format(KEMONOMIMI_KEY)

SAUCE_LINES = [THIGH_CONFIG, FEET_CONFIG, CUTE_GIRLS_MOE_CONFIG, KEMONOMIMI_CONFIG]
SAUCE_LINKS = [THIGH_LINKS , FEET_LINKS , CUTE_GIRLS_MOE_LINKS , KEMONOMIMI_LINKS ]
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

    for i in SAUCE_LINES:
        os.makedirs(os.path.dirname(i), exist_ok=True)

        if not os.path.isfile(i):
            with open(i, "w") as writer:
                writer.write("")

    for i in SAUCE_LINKS:

            if not os.path.isfile(i):
                with open(i, "w") as writer:
                    writer.write("")

    