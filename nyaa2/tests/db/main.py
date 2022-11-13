
import sqlite3
import threading

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
            
            raise exception

        finally:
            self.lock.release ()

    def execute_select_one(self, *args):

        self.lock.acquire ()
        
        try:
            self.cursor.execute (*args)

            return self.cursor.fetchone ()

        except Exception as exception:
            
            raise exception

        finally:
            self.lock.release ()

    def execute (self, *args):
        self.lock.acquire ()

        try:
            self.cursor.execute (*args)

        except Exception as exception:
            
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

    def __enter__(self):

        self.cursor.execute("BEGIN")

        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_traceback):

        if exc_type:
            
            self.cursor.execute("ROLLBACK")

        else:

            self.cursor.execute("COMMIT")


class MiscDB(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if MiscDB.__INSTANCE == None:
            MiscDB()

        return MiscDB.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if MiscDB.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, ".\\db.db")
        MiscDB.__INSTANCE = self


    def create_tables(self):
        
        if not self.connection:
            self.connect()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_trusted" (
            "user_id" INTEGER PRIMARY KEY NOT NULL,
            "username" VARCHAR
        );""")

        self.commit()

        
    def add_trusted_user(self, username, user_id):

        self.cursor.execute("INSERT OR IGNORE INTO tbl_trusted VALUES (?, ?)", (user_id, username))


    def remove_trusted_user(self, user_id):
    
        self.cursor.execute("DELETE FROM tbl_trusted WHERE user_id = ?", (user_id, ))

    
    def is_user_trusted(self, user_id):

        row = self.cursor.execute_select_one("SELECT * FROM tbl_trusted WHERE user_id = ?", (user_id,))

        if not row:

            return False 

        return True 

    def get_all_trusted(self):

        return self.cursor.execute_select_all("SELECT * FROM tbl_trusted")


    def add_stuff(self):

        with self as cursor:

            # for i in range(10):

                # cursor.execute("DELETE FROM tbl_trusted WHERE user_id = ?", (i,))
                # cursor.execute("INSERT INTO tbl_trusted VALUES (?, ?)", (10+i, "sex"))
                # cursor.execute("UPDATE tbl_trusted SET username = 'sex' WHERE user_id = ?", (i,))

                # print(cursor.cursor.lastrowid)

            cursor.execute("DELETE FROM tbl_trusted WHERE rowid NOT IN (SELECT MIN(rowid) FROM tbl_trusted GROUP BY username)")


if __name__ == "__main__":

    instance = MiscDB.get_instance()
    instance.connect()
    instance.create_tables()

    instance.add_stuff()