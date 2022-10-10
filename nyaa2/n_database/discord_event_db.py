
import typing
import datetime

from .. import constants

from .db import * 

class DiscordEventDB(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if DiscordEventDB.__INSTANCE == None:
            DiscordEventDB()

        return DiscordEventDB.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if DiscordEventDB.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, constants.DATABASE_PATH)
        DiscordEventDB.__INSTANCE = self


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

        # self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_reaction_role" (
        #     "reaction_role_id" INTEGER PRIMARY KEY NOT NULL,
        #     "reaction_role_channel_id" INTEGER,
        #     "reaction_role_role_id" INTEGER,
        #     "reaction_role_message_id" INTEGER,
        #     "reaction_role_emote" VARCHAR,
        #     FOREIGN KEY(reaction_role_channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE
        # );""")

        self.commit()


    def add_server(self, server_id : int, 
                   server_name : str, 
                   server_owner_id : int,
                   server_date_created : typing.Union[int, datetime.datetime]):

        row = self.cursor.execute_select_one("SELECT server_id FROM tbl_server WHERE server_id=?", (server_id,))

        if row:
            return -1

        if server_date_created :

            if isinstance(server_date_created, datetime.datetime):

                server_date_created = int(server_date_created.timestamp())
        
        else:

            server_date_created = int(datetime.datetime.now().timestamp())


        self.cursor.execute("INSERT INTO tbl_server values (?, ?, ?, ?)", (server_id, server_name, server_date_created, server_owner_id))

        return self.cursor.cursor.lastrowid

    

    def add_channel(self, server_id : int, 
                    channel_id : int, 
                    channel_name : str,
                    channel_type : int):
        
        row = self.cursor.execute_select_one("SELECT * FROM tbl_server_channel WHERE channel_id = ?", (channel_id,))

        if row:

            self.cursor.execute("UPDATE tbl_channel SET channel_name = ? WHERE channel_id = ?", (channel_name, channel_id))
            return row['server_channel_id']

        self.cursor.execute("INSERT INTO tbl_channel values (?, ?, ?)", (channel_id, channel_name, channel_type))
            
        self.cursor.execute("INSERT OR IGNORE INTO tbl_server_channel (server_id, channel_id) values (?, ?) ", (server_id, channel_id))

        return self.cursor.cursor.lastrowid




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


