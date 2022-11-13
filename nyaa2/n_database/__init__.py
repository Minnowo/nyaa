

from .db import * 
from .discord_event_db import *
from .media_url_db import * 
from .discord_log_db import *
from .misc_db import *



# try:
#     from .. import constants

# except:

#     class constants:
#         DATABASE_PATH = ".\\sample.db"
#         DATABASE_IMAGES_PATH= ".\\images.db"

# def add_test():

    
#     db_instance = Image_Tables.get_instance()
#     db_instance.connect()
#     db_instance.create_tables()


#     db_instance.add_image_category("astolfo")
#     EVENT = db_instance.select_category_id_by_name("astolfo")

#     db_instance.add_image(EVENT, "https://uwu.com", 0)

#     # db_instance.add_server(56, "servername", 1123, 0)
#     # db_instance.add_channel(56, 92, "channel name", 0)
#     # db_instance.add_channel_event(92, EVENT)

#     # db_instance.commit()

#     CONFIG_FORMAT = "config\\sauce\\{0}\\{0}_lines.json"
#     LINKS_SFW_FORMAT = "config\\sauce\\{0}\\{0}_links_sfw.txt"
#     LINKS_NSFW_FORMAT = "config\\sauce\\{0}\\{0}_links_nsfw.txt"

#     LINK_FILE_END   = "--links-end--"

#     MODULES = ["appleworm", "bondage", "cutegirls", "feet", "femboy", "fubuki", "gura", "hutao", 
#             "kemonomimi", "mori", "navel", "okayu", "panties", "pekora", "rushia", "suisei", 
#             "thighs", "witch", "nyaa", "ranni", "laplus", "subaru", "baelz"]


#     for i in MODULES:

#         cate = db_instance.add_image_category(i)
#         cat = db_instance.select_category_id_by_name(i)
#         print("adding category: " + i)
#         path = "..\\" + LINKS_SFW_FORMAT.format(i)


#         with open(path, "r") as reader:
            
#             for line in reader:

#                 if line.startswith("http"):
#                     db_instance.add_image(cat, line.strip(), 0)
#                     print("adding {}".format(line.strip()))

#         path = "..\\" + LINKS_NSFW_FORMAT.format(i)

#         with open(path, "r") as reader:
            
#             for line in reader:

#                 if line.startswith("http"):

#                     db_instance.add_image(cat, line.strip(), 1)
#                     print("adding {}".format(line.strip()))

#         db_instance.commit()

# add_test()