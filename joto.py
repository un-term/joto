import sqlite3
import datetime
import os
import subprocess
from pathlib import Path
import sqlite3
import shutil

class SQLiteDB():
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.connection = None
        self.changes = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db)
            return self.connection.cursor()
            print("Successfully connected to: ",self.db)

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)

    def disconnect(self,cursor):
        try:
            cursor.close()
            self.changes = self.connection.total_changes
            self.connection.close()
            print("SQLite connection is closed")
        except sqlite3.Error as error:
            print("Error disconnecting from SQLite db", error)

    def check_for_table(self):
        cursor = self.connect()
        
        # sqlite_query = '''SELECT name FROM sqlite_master WHERE type='table' AND name='{''' + self.table + '''}';'''
        sqlite_query = ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=' ''' + self.table + ''' ' ;'''
        cursor.execute(sqlite_query)
        if not cursor.fetchone()[0] == 1:
            raise Exception("Table does not exist: ", self.table)

        self.disconnect(cursor)

    def create_db_table(self):
        cursor = self.connect()

        # sqlite_create_table_query = '''CREATE TABLE joto (
        #                         id    INTEGER PRIMARY KEY AUTOINCREMENT,
        #                         title TEXT NOT NULL,
        #                         date  TEXT NOT NULL,
        #                         text  TEXT NOT NULL,
        #                         image TEXT NOT NULL
        #                     );'''
        sqlite_create_table_query = '''CREATE TABLE ''' + self.table + ''' (
                                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT NOT NULL,
                                date  TEXT NOT NULL,
                                text  TEXT NOT NULL,
                                image TEXT NOT NULL
                            );'''

        cursor.execute(sqlite_create_table_query)
        self.connection.commit()
        print("SQLite table created")

        self.disconnect(cursor)

    def add_joto_data(self, title, date, text, image):
        cursor = self.connect()

        sqlite_insert_with_param = '''INSERT INTO ''' + self.table + '''
                          (title, date, text, image) 
                          VALUES (?, ?, ?, ?);'''

        data_tuple = (title, date, text, image)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        self.connection.commit()
        print("Python Variables inserted successfully into joto table")

        self.disconnect(cursor)

    def retrieve_all_data_ordered_by_date(self):
        cursor = self.connect()

        sqlite_select_query = '''SELECT * from ''' + self.table + '''
                                    ORDER BY date ASC;'''
        cursor.execute(sqlite_select_query)
        return cursor.fetchall()
          
        self.disconnect(cursor)

    def export_text_to_files(self):
        pass

    def remove_last_row():
        pass

    def check_image_file():
        pass

class ImagesManage():
    def __init__(self,size, src_dir, dst_dir, achv_dir):
        # self.compression_size = "1000x1000"
        # self.src_dir = "ingest_images/"
        # self.dst_dir = "images/compressed/"
        self.size = size #compression size
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.achv_dir = achv_dir
        self.file_types = ["jpg","JPG","jpeg","JPEG","png","PNG"]

    def compress_image(self, name):
        src_filepath = self.src_dir + name
        dst_filepath = self.dst_dir + name
        achv_filepath = self.achv_dir + name
        self._check_filetype(name)
        try:
            subprocess.run(["convert", "-resize", self.size, src_filepath, dst_filepath], check=True)
        except: raise Exception("External Image Magik convert failed")
        finally: self._keep_original_image(src_filepath, achv_filepath)

    def _keep_original_image(self, src_filepath, dst_filepath):
            shutil.move(src_filepath, dst_filepath)

    def _check_filetype(self,name):
        check = False
        for ext in self.file_types:
            if name.endswith(ext):
                check = True
        if not check: raise Exception("Error: Incorrect file type")


class Joto():
    def __init__(self, sqlite_db, images_manage, ):

        self.sqlite_db = sqlite_db
        self.images_manage = images_manage

    def add_text_only(self):
        pass

    def scan_for_and_add_images_with_text(self):

        for root, dirs, files in os.walk(ingest_dir): 
            for file in files:
                if self.check_file_types(file):
                    pass

def main():
    db_path = "joto.db"
    table = '''joto'''
    src_dir = "ingest_images/"
    dst_dir = "images/compressed/"
    achv_dir = "images/original"
    size = "1000x1000"
    

    sqlite_db = SQLiteDB(db_path,table)
    images_manage = ImagesManage()


if __name__ == "__main__":
    main()
