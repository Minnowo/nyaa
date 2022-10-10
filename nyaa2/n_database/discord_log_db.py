
import typing
import datetime

from .. import constants

from .db import * 

class DiscordLogDB(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if DiscordLogDB.__INSTANCE == None:
            DiscordLogDB()

        return DiscordLogDB.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if DiscordLogDB.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, constants.DATABASE_LOG_PATH)
        DiscordLogDB.__INSTANCE = self


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

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_message" (
            "message_id" INTEGER PRIMARY KEY NOT NULL,
            "message_content" BLOB,
            "message_time" INTEGER
        );""")

        # channel_type : 0 = text, 1 = voice
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_channel" (
            "channel_id" INTEGER PRIMARY KEY NOT NULL,
            "channel_name" VARCHAR
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_user" (
            "user_id" INTEGER PRIMARY KEY NOT NULL,
            "username" VARCHAR
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_attachments" (
            "attachment_id" INTEGER PRIMARY KEY NOT NULL,
            "message_id" INTEGER,
            "attachment_url" VARCHAR,
            "attachment_proxy_url" VARCHAR,
            FOREIGN KEY(message_id) REFERENCES tbl_message(message_id) ON DELETE CASCADE,
            UNIQUE (attachment_id, message_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server_channel" (
            "server_channel_id" INTEGER PRIMARY KEY NOT NULL,
            "server_id" INTEGER,
            "channel_id" INTEGER,
            FOREIGN KEY(server_id) REFERENCES tbl_server(server_id) ON DELETE CASCADE,
            FOREIGN KEY(channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE,
            UNIQUE (server_id, channel_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_user_message" (
            "user_message_id" INTEGER PRIMARY KEY NOT NULL,
            "user_id" INTEGER,
            "message_id" INTEGER,
            FOREIGN KEY(user_id) REFERENCES tbl_user(user_id) ON DELETE CASCADE,
            FOREIGN KEY(message_id) REFERENCES tbl_message(message_id) ON DELETE CASCADE,
            UNIQUE (user_id, message_id)
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_server_channel_message" (
            "server_channel_id" INTEGER,
            "user_message_id" INTEGER,
            FOREIGN KEY(server_channel_id) REFERENCES tbl_server_channel(server_channel_id) ON DELETE CASCADE,
            FOREIGN KEY(user_message_id) REFERENCES tbl_user_message(user_message_id) ON DELETE CASCADE,
            PRIMARY KEY (server_channel_id, user_message_id)
        );""")

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
                    channel_name : str):
        
        row = self.cursor.execute_select_one("SELECT * FROM tbl_server_channel WHERE channel_id = ?", (channel_id,))

        if row:

            self.cursor.execute("UPDATE tbl_channel SET channel_name = ? WHERE channel_id = ?", (channel_name, channel_id))
            
            return row['server_channel_id']


        self.cursor.execute("INSERT INTO tbl_channel values (?, ?)", (channel_id, channel_name))
        
        self.cursor.execute("INSERT INTO tbl_server_channel (server_id, channel_id) values (?, ?) ", (server_id, channel_id))

        return self.cursor.cursor.lastrowid



    def add_user(self, username : int, user_id : int = -1):

        row = self.cursor.execute_select_one("SELECT user_id FROM tbl_user WHERE user_id = ?", (user_id,))

        if row:

            self.cursor.execute("UPDATE tbl_user SET username = ? WHERE user_id = ?", (username, user_id))

            return row['user_id'] 

        self.cursor.execute("INSERT INTO tbl_user values (?, ?)", (user_id, username))

        return self.cursor.cursor.lastrowid



    def add_channel_message_user(self, message):

        user_id = message.author.id 
        username = message.author.name 

        channel_id = message.channel.id 
        channel_name = message.channel.name

        server_id = message.guild.id 

        message_id = message.id
        message_content = message.content.encode()

        self.add_user(username, user_id)

        server_channel_id = self.add_channel(server_id, channel_id, channel_name)

        self.cursor.execute("INSERT INTO tbl_message VALUES (?, ?, ?)", (message_id, message_content, int(message.created_at.timestamp())))

        self.cursor.execute("INSERT INTO tbl_user_message (user_id, message_id) VALUES (?, ?)", (user_id, message_id))

        user_msg_id = self.cursor.cursor.lastrowid

        self.cursor.execute("INSERT INTO tbl_server_channel_message VALUES (?, ?)", (server_channel_id, user_msg_id))

        for attachment in message.attachments:

            self.cursor.execute("INSERT INTO tbl_attachments (message_id, attachment_url, attachment_proxy_url) VALUES (?, ?, ?)", (message.id, attachment.url, attachment.proxy_url))
