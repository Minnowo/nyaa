

from .. import constants

from .db import * 

class MediaUrlDB(DB):

    __INSTANCE = None 

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if MediaUrlDB.__INSTANCE == None:
            MediaUrlDB()

        return MediaUrlDB.__INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        
        if MediaUrlDB.__INSTANCE != None:
            raise Exception("This class is a singleton!")
        
        DB.__init__(self, constants.DATABASE_IMAGES_PATH)
        MediaUrlDB.__INSTANCE = self


    def create_tables(self):
        
        if not self.connection:
            self.connect()
        
        with self:

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

    def update_image_sfw_type(self, image_id, is_nsfw):

        is_nsfw = 1 if is_nsfw else 0
        
        self.cursor.execute("UPDATE OR IGNORE tbl_image SET is_nsfw = ? WHERE image_id = ?", (is_nsfw, image_id))

    def get_image(self, category_id):

        return self.cursor.execute_select_one("select * from tbl_image JOIN tbl_image_category USING(image_id) WHERE category_id = ? order by RANDOM();", (category_id,))


    def get_images(self, category_id, count):

        return self.cursor.execute_select_all("select * from tbl_image JOIN tbl_image_category USING(image_id) WHERE category_id = ? order by RANDOM() LIMIT ?", (category_id, count))


    def get_images_with_rating(self, category_id, count, is_nsfw):

        is_nsfw = 1 if is_nsfw else 0

        return self.cursor.execute_select_all("select * from tbl_image JOIN tbl_image_category USING(image_id) WHERE category_id = ? AND is_nsfw = ? order by RANDOM() LIMIT ?", (category_id, is_nsfw, count))


    def get_all_categories(self):

        return self.cursor.execute_select_all("select * from tbl_category")


    def remove_duplicate_url(self):

        self.cursor.execute("DELETE FROM tbl_image WHERE rowid NOT IN (SELECT MIN(rowid) FROM tbl_image GROUP BY image_url)")