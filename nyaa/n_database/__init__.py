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

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if DB.__INSTANCE == None:
            DB()

        return DB.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if DB.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__INSTANCE = self


    def connect (self):
        self.connection = get_connection(constants.DATABASE_PATH)
        self.connection.row_factory = dict_factory
        self.cursor = LockableCursor (self.connection.cursor ())

    def commit(self):
        self.connection.commit()

    def close(self):

        self.connection.commit()
        self.cursor.close()
        self.connection.close()
    

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
            FOREIGN KEY(server_id) REFERENCES tbl_server(server_id) ON DELETE CASCADE
            FOREIGN KEY(channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE
            UNIQUE (server_id, channel_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server_channel_event" (
            "server_channel_id" INTEGER,
            "event_id" INTEGER,
            FOREIGN KEY(server_channel_id) REFERENCES tbl_server_channel(server_channel_id) ON DELETE CASCADE
            FOREIGN KEY(event_id) REFERENCES tbl_event(event_id) ON DELETE CASCADE
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


        self.connection.commit()


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




def add_test():

    
    db_instance = DB.get_instance()
    db_instance.connect()
    db_instance.create_tables()


    db_instance.add_event("uwu")
    EVENT = db_instance.select_event_id_by_name("uwu")

    # db_instance.add_server(56, "servername", 1123, 0)
    # db_instance.add_channel(56, 92, "channel name", 0)
    # db_instance.add_channel_event(92, EVENT)

    # db_instance.commit()

    db_instance.remove_channel_event(92, EVENT)


add_test()