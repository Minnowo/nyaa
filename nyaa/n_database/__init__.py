import sqlite3
import os 
import typing
import datetime
import threading

try:
    from .. import constants

except:

    class constants:
        DATABASE_PATH = ".\\sample.db"
        DATABASE_IMAGES_PATH= ".\\images.db"

def dict_factory (cursor, row):
    aDict = {}
    for iField, field in enumerate (cursor.description):
        aDict [field [0]] = row [iField]
    return aDict


def get_connection(database_path : str, foreign_key_checks=True, check_same_thread=False, isolation_level=None):
    
    conn = sqlite3.connect(database_path, check_same_thread=check_same_thread, isolation_level=isolation_level)

    if foreign_key_checks:
    
        conn.execute('pragma foreign_keys = ON')

    return conn


class LockableCursor:

    def __init__ (self, cursor):
        self.cursor = cursor
        self.lock = threading.Lock ()

    def close(self):
        self.cursor.close()

    def execute_select_all(self, *args):

        self.lock.acquire ()
        
        try:
            self.cursor.execute (*args)

            return self.cursor.fetchall ()

        except Exception as exception:
            print(args)
            raise exception

        finally:
            self.lock.release ()

    def execute_select_one(self, *args):

        self.lock.acquire ()
        
        try:
            self.cursor.execute (*args)

            return self.cursor.fetchone ()

        except Exception as exception:
            print(args)
            raise exception

        finally:
            self.lock.release ()

    def execute (self, *args):
        self.lock.acquire ()

        try:
            self.cursor.execute (*args)

        except Exception as exception:
            print(args)
            raise exception

        finally:
            self.lock.release ()



class DB():

    def __init__(self, db_path) -> None:
        self.db_path = db_path

    def connect (self):
        self.connection = get_connection(self.db_path)
        self.connection.row_factory = dict_factory
        self.cursor = LockableCursor (self.connection.cursor ())

    def commit(self):
        self.connection.commit()

    def close(self):

        self.connection.commit()
        self.cursor.close()
        self.connection.close()



class Image_Tables(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if Image_Tables.__INSTANCE == None:
            Image_Tables()

        return Image_Tables.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if Image_Tables.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, constants.DATABASE_IMAGES_PATH)
        Image_Tables.__INSTANCE = self


    def create_tables(self):
        
        if not self.connection:
            self.connect()
        

        # is_nsfw : 0 = false 1 = true 
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_image" (
            "image_id" INTEGER PRIMARY KEY NOT NULL,
            "image_url" VARCHAR,
            "is_nsfw" INTEGER
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_category" (
            "category_id" INTEGER PRIMARY KEY NOT NULL,
            "category_name" VARCHAR UNIQUE
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_image_category" (
            "category_id" INTEGER,
            "image_id" INTEGER,
            FOREIGN KEY(category_id) REFERENCES tbl_category(category_id) ON DELETE CASCADE,
            FOREIGN KEY(image_id) REFERENCES tbl_image(image_id) ON DELETE CASCADE,
            PRIMARY KEY (category_id, image_id)
        );""")

        self.commit()

        
    def add_image_category(self, category_name):

        self.cursor.execute("INSERT OR IGNORE INTO tbl_category (category_name) values (?)", (category_name,))


    def add_image(self, category_id, image_url, is_nsfw):
            
        self.cursor.execute("INSERT INTO tbl_image (image_url, is_nsfw) values (?, ?)", (image_url, is_nsfw))

        id = self.cursor.cursor.lastrowid
        
        self.cursor.execute("INSERT OR IGNORE INTO tbl_image_category values (?, ?)", (category_id, id))


    def select_category_by_name(self, category_name : str):

        return self.cursor.execute_select_one("SELECT * FROM tbl_category WHERE category_name = ?", (category_name,))


    def select_category_id_by_name(self, category_name : str):

        row = self.cursor.execute_select_one("SELECT category_id FROM tbl_category WHERE category_name = ?", (category_name,))
        
        if row:
            return row["category_id"]

        return None 





class Discord_Tables(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if Discord_Tables.__INSTANCE == None:
            Discord_Tables()

        return Discord_Tables.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if Discord_Tables.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, constants.DATABASE_PATH)
        Discord_Tables.__INSTANCE = self


    def create_tables(self):

        if not self.connection:
            self.connect()
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server" (
            "server_id" INTEGER PRIMARY KEY NOT NULL,
            "server_name" VARCHAR,
            "server_date_created" INTEGER,
            "server_owner_id" INTEGER
        );
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_event" (
            "event_id" INTEGER PRIMARY KEY NOT NULL,
            "event_name" VARCHAR UNIQUE
        );""")

        # channel_type : 0 = text, 1 = voice
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_channel" (
            "channel_id" INTEGER PRIMARY KEY NOT NULL,
            "channel_name" VARCHAR,
            "channel_type" INTEGER
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server_channel" (
            "server_channel_id" INTEGER PRIMARY KEY NOT NULL,
            "server_id" INTEGER,
            "channel_id" INTEGER,
            FOREIGN KEY(server_id) REFERENCES tbl_server(server_id) ON DELETE CASCADE,
            FOREIGN KEY(channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE,
            UNIQUE (server_id, channel_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server_channel_event" (
            "server_channel_id" INTEGER,
            "event_id" INTEGER,
            FOREIGN KEY(server_channel_id) REFERENCES tbl_server_channel(server_channel_id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES tbl_event(event_id) ON DELETE CASCADE,
            PRIMARY KEY (server_channel_id, event_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_reaction_role" (
            "reaction_role_id" INTEGER PRIMARY KEY NOT NULL,
            "reaction_role_channel_id" INTEGER,
            "reaction_role_role_id" INTEGER,
            "reaction_role_message_id" INTEGER,
            "reaction_role_emote" VARCHAR,
            FOREIGN KEY(reaction_role_channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE
        );""")

        self.commit()


    def add_server(self, server_id : int, 
                   server_name : str, 
                   server_owner_id : int,
                   server_date_created : typing.Union[int, datetime.datetime]):

        row = self.cursor.execute_select_one("SELECT server_id FROM tbl_server WHERE server_id=?", (server_id,))

        if row:

            self.cursor.execute("UPDATE tbl_server SET server_name = ?, server_owner_id = ? WHERE server_id = ?", (server_name, server_owner_id, server_id))
            return 

        if server_date_created :

            if isinstance(server_date_created, datetime.datetime):

                server_date_created = int(server_date_created.timestamp())
        
        else:

            server_date_created = int(datetime.datetime.now().timestamp())


        self.cursor.execute("INSERT INTO tbl_server values (?, ?, ?, ?)", (server_id, server_name, server_date_created, server_owner_id))


    def add_channel(self, server_id : int, 
                    channel_id : int, 
                    channel_name : str,
                    channel_type : int):
        
        row = self.cursor.execute_select_one("SELECT channel_id FROM tbl_channel WHERE channel_id = ?", (channel_id,))

        if row:

            self.cursor.execute("UPDATE tbl_channel SET channel_name = ? WHERE channel_id = ?", (channel_name, channel_id))
            
        else:

            self.cursor.execute("INSERT INTO tbl_channel values (?, ?, ?)", (channel_id, channel_name, channel_type))
            
        self.cursor.execute("INSERT OR IGNORE INTO tbl_server_channel (server_id, channel_id) values (?, ?) ", (server_id, channel_id))


    def add_event(self, event_name : int, event_id : int = -1):

        if event_id == -1:
            self.cursor.execute("INSERT OR IGNORE INTO tbl_event (event_name) values (?)", (event_name,))
        
        else:
            self.cursor.execute("INSERT OR IGNORE INTO tbl_event values (?, ?)", (event_id, event_name))


    def add_channel_event(self, channel_id : int, event_id : int):

        row = self.cursor.execute_select_one("SELECT server_channel_id FROM tbl_server_channel WHERE channel_id = ?", (channel_id,))

        if not row:
            return 

        id = row["server_channel_id"]

        self.cursor.execute("INSERT OR IGNORE INTO tbl_server_channel_event values (?, ?)", (id, event_id))

    def remove_channel_event(self, channel_id : int, event_id : int):

        self.cursor.execute("DELETE FROM tbl_server_channel_event WHERE server_channel_id IN (SELECT server_channel_id FROM tbl_server_channel WHERE channel_id = ?) AND event_id = ?", (channel_id, event_id))
    
    def remove_channel_event_2(self, server_id : int, channel_id : int, event_id : int):

        self.cursor.execute("DELETE FROM tbl_server_channel_event WHERE server_channel_id IN (SELECT server_channel_id FROM tbl_server_channel WHERE channel_id = ? AND server_id = ?) AND event_id = ?", (channel_id, server_id, event_id))

    def add_reaction_role(self, channel_id : int, role_id : int, message_id : int, emote : str):

        self.cursor.execute("INSERT INTO tbl_reaction_role (reaction_role_channel_id, reaction_role_role_id, reaction_role_message_id, reaction_role_emote) values (?, ?, ?, ?)", (channel_id, role_id, message_id, emote))


    def select_event_by_name(self, event_name : str):

        return self.cursor.execute_select_one("SELECT * FROM tbl_event WHERE event_name = ?", (event_name,))


    def select_event_id_by_name(self, event_name : str):

        row = self.cursor.execute_select_one("SELECT event_id FROM tbl_event WHERE event_name = ?", (event_name,))
        
        if row:
            return row["event_id"]

        return None 


    def channel_has_event(self, channel_id : int, event_id : int):

        row = self.cursor.execute_select_one("SELECT server_channel_id FROM tbl_server_channel WHERE channel_id = ?", (channel_id,))

        if not row:
            return False 

        id = row["server_channel_id"]

        return self.cursor.execute_select_one("SELECT channel_id FROM tbl_server_channel_event WHERE server_channel_id = ? AND event_id = ?", (id, event_id)) is not None 

    def select_channels_where_event(self, server_id, event_id):

        return self.cursor.execute_select_all("SELECT channel_id FROM tbl_server_channel JOIN tbl_server_channel_event USING(server_channel_id) WHERE server_id = ? AND event_id = ?", (server_id, event_id))




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