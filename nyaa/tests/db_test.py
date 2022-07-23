import sqlite3
import os 
import typing
import datetime

def create_tables(connection):
    
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE "tbl_server" (
        "server_id" INTEGER PRIMARY KEY NOT NULL,
        "server_name" VARCHAR,
        "server_date_created" INTEGER,
        "server_owner_id" INTEGER
    );
    """)

    cursor.execute("""CREATE TABLE "tbl_event" (
        "event_id" INTEGER PRIMARY KEY NOT NULL,
        "event_name" VARCHAR
    );""")

    # channel_type : 0 = text, 1 = voice
    cursor.execute("""CREATE TABLE "tbl_channel" (
        "server_id" INTEGER,
        "channel_id" INTEGER,
        "channel_name" VARCHAR,
        "channel_type" INTEGER,
        FOREIGN KEY(server_id) REFERENCES tbl_server(server_id) ON DELETE CASCADE
        PRIMARY KEY (server_id, channel_id)
    );""")

    cursor.execute("""CREATE TABLE "tbl_channel_event" (
        "channel_id" INTEGER,
        "event_id" INTEGER,
        FOREIGN KEY(channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE
        FOREIGN KEY(event_id) REFERENCES tbl_event(event_id) ON DELETE CASCADE
        PRIMARY KEY (channel_id, event_id)
    );""")

    cursor.execute("""CREATE TABLE "tbl_reaction_role" (
        "reaction_role_id" INTEGER PRIMARY KEY NOT NULL,
        "reaction_role_channel_id" INTEGER,
        "reaction_role_role_id" INTEGER,
        "reaction_role_message_id" INTEGER,
        "reaction_role_emote" VARCHAR,
        FOREIGN KEY(reaction_role_channel_id) REFERENCES tbl_channel(channel_id) ON DELETE CASCADE
    );""")


    connection.commit()


def add_server(server_id : int, 
               server_name : str, 
               server_owner_id : int,
               server_date_created : typing.Union[int, datetime.datetime], 
               *,
               cursor):

    cursor.execute("SELECT server_id FROM tbl_server WHERE server_id=?", (server_id,))
    row = cursor.fetchone()

    if row:

        cursor.execute("UPDATE tbl_server SET server_name = ?, server_owner_id = ? WHERE server_id = ?", (server_name, server_owner_id, server_id))
        return 

    if server_date_created :

        if isinstance(server_date_created, datetime.datetime):

            server_date_created = int(server_date_created.timestamp())
    
    else:

        server_date_created = int(datetime.datetime.now().timestamp())


    cursor.execute("INSERT INTO tbl_server values (?, ?, ?, ?)", (server_id, server_name, server_date_created, server_owner_id))


def add_channel(server_id : int, 
                channel_id : int, 
                channel_name : str,
                channel_type : int,
                *,
                cursor):

    cursor.execute("SELECT server_id, channel_id FROM tbl_channel WHERE server_id = ? AND channel_id = ?", (server_id, channel_id))
    row = cursor.fetchone()

    if row:

        cursor.execute("UPDATE tbl_channel SET channel_name = ? WHERE server_id = ? AND channel_id = ?", (channel_name, server_id, channel_id))
        return 

    cursor.execute("INSERT INTO tbl_channel values (?, ?, ?, ?)", (server_id, channel_id, channel_name, channel_type))


def add_event(event_name : int, event_id : int = -1, *, cursor):

    if event_id == -1:
        cursor.execute("INSERT OR IGNORE INTO tbl_event (event_name) values (?)", (event_name,))
    
    else:
        cursor.execute("INSERT OR IGNORE INTO tbl_event values (?, ?)", (event_id, event_name))


def add_channel_event(channel_id : int, event_id : int, *, cursor):

    cursor.execute("INSERT OR IGNORE INTO tbl_channel_event values (?, ?)", (channel_id, event_id))


def add_reaction_role(channel_id : int, role_id : int, message_id : int, emote : str, *, cursor):

    cursor.execute("INSERT INTO tbl_reaction_role (reaction_role_channel_id, reaction_role_role_id, reaction_role_message_id, reaction_role_emote) values (?, ?, ?, ?)", (channel_id, role_id, message_id, emote))


def get_connection(database_path : str, foreign_key_checks=True):
    
    conn = sqlite3.connect(database_path)

    if foreign_key_checks:
    
        conn.execute('pragma foreign_keys = ON')

    return conn

DB_PATH = ".\\sample.db"

if os.path.isfile(DB_PATH):
    os.unlink(DB_PATH)

servers = sqlite3.connect(DB_PATH)

cursor = servers.cursor()
create_tables(servers)
add_server(12345, "sample server name", 1337, datetime.datetime.now(), cursor=cursor)

servers.commit()

add_server(12345, "new server name", 8888, datetime.datetime.now(), cursor=cursor)
servers.commit()

add_channel(12345, 6969, "channel name", 0, cursor=cursor)

add_event("user_leave", cursor=cursor)
add_event("user_join", cursor=cursor)
add_channel_event(6969, 0, cursor=cursor)
add_channel_event(6969, 1, cursor=cursor)

add_reaction_role(12345, 1, 1, "here is an emote", cursor=cursor)
add_reaction_role(1222345, 1, 1, "here is an emote", cursor=cursor)
servers.commit()
