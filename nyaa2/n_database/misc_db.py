

from .. import constants

from .db import * 

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
        
        DB.__init__(self, constants.DATABASE_MISC_PATH)
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