#!/usr/bin/env python

import sqlite3
import datetime
import os
import subprocess
from pathlib import Path
import sqlite3
import shutil


class JotoSQLiteDB():
    '''Performs fixed sql operations on joto table'''
    def __init__(self, db_path):
        self.db = db_path
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

    def check_db_path(self):
        if os.path.exists(self.db): return True
        else: return False

    def check_for_table(self):
        cursor = self.connect()
        
        # sqlite_query = '''SELECT name FROM sqlite_master WHERE type='table' AND name='{''' + self.table + '''}';'''
        sqlite_query = ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='joto'; '''
        cursor.execute(sqlite_query)
        if cursor.fetchone()[0] == 1: return True
        elif cursor.fetchone()[0] == 0: return False

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
        sqlite_create_table_query = '''CREATE TABLE joto (
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

        sqlite_insert_with_param = '''INSERT INTO joto
                          (title, date, text, image) 
                          VALUES (?, ?, ?, ?);'''

        data_tuple = (title, date, text, image)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        self.connection.commit()
        print(f"Adding {title} to db")

        self.disconnect(cursor)

    def retrieve_all_data_ordered_by_date(self):
        cursor = self.connect()

        sqlite_select_query = '''SELECT * from joto
                                    ORDER BY date ASC;'''
        cursor.execute(sqlite_select_query)
        return cursor.fetchall()
          
        self.disconnect(cursor)

    def export_text_to_files(self):
        pass

    def remove_last_row():
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
        self.target_size = 20 #%

    def check_paths(self):
        count = 3
        if os.path.exists(self.src_dir): count -= 1
        if os.path.exists(self.dst_dir): count -= 1
        if os.path.exists(self.achv_dir): count -= 1
        if count == 0: return True
        else: return False

    def create_paths(self):
        os.makedirs(self.src_dir)
        os.makedirs(self.dst_dir)
        os.makedirs(self.achv_dir)

    def compress_and_archive_image(self,name):
        src_filepath = self.src_dir + name
        dst_filepath = self.dst_dir + name
        achv_filepath = self.achv_dir + name

        self._compress_image(src_filepath,dst_filepath)
        if self._check_compression(src_filepath,dst_filepath):
            self._archive_original_image(src_filepath,achv_filepath)        
        else: raise Exception("Compression not worked")

    def _compress_image(self,src_filepath,dst_filepath):
        try:
            subprocess.run(["convert", "-resize", self.size, src_filepath, dst_filepath], check=True)
        except: raise Exception("External Image Magik convert failed")

    def _check_compression(self,src_filepath,dst_filepath):
        original_image_size = int(os.stat(src_filepath)[6])
        compressed_image_size = int(os.stat(dst_filepath)[6])
        if (compressed_image_size/original_image_size) < (self.target_size/100):
            return True
        
    def _archive_original_image(self, src_filepath, achv_filepath):
            shutil.move(src_filepath, achv_filepath)

    def check_filetype(self,name):
        check = False
        for ext in self.file_types:
            if name.endswith(ext):
                check = True
        if not check: raise Exception("Error: Incorrect file type")

class TextInput():

    def get_input(self):
        return input("Text: ")


class Joto():
    def __init__(self, sqlite_db, images_manage, text_input):

        self.sqlite_db = sqlite_db
        self.images_manage = images_manage
        self.text_input = text_input

    def check_requirements(self):
        '''Not to be used as part of other functions - manual intervention required'''
        if self.sqlite_db.check_db_path() and self.sqlite_db.check_for_table() and self.images_manage.check_paths():
            print("Requirements met!")
        else: raise Exception("Requiements at NOT met")

    def create_all_requirements(self):
        self.sqlite_db.create_db_table()
        self.images_manage.create_paths()
        print("db,table and paths created")

    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

    def extract_attributes(self, file):
        title = os.path.splitext(file)[0]
        date = title[:10]
        self.validate(date)
        return title,date

    def add_text_only(self):
        pass

    def scan_for_and_add_images_with_text(self):
        for root, dirs, files in os.walk(self.images_manage.src_dir): 
            for file in files:
                self.images_manage.check_filetype(file)
                title,date = self.extract_attributes(file)
                print(title)
                text = self.text_input.get_input()
                self.sqlite_db.add_joto_data(title,date,text,file)

                self.images_manage.compress_and_archive_image(file)

    def export_text(path):
        pass

# def main():
#     db_path = "joto.db"
#    = "ingest_images/"
#     dst_dir = "images/compressed/"
#     achv_dir = "images/original"
#     size = "1000x1000"
    
#     sqlite_db = JotoSQLiteDB(db_path)
#     images_manage = ImagesManage(size, dst_dir, achv_dir)
#     joto = Joto(sqlite_db, images_manage,src_dir)
#     joto.scan_for_and_add_images_with_text()


# if __name__ == "__main__":
#   images_manage.src_dir main(images_manage.src_dir
