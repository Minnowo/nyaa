

from .. import constants

from .db import * 

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

