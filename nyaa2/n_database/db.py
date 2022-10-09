
import sqlite3
import threading

from .. import util
from .. import constants


DB_BASE_LOGGER = util.get_logger(*constants.DB_BASE_LOGGER)


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
