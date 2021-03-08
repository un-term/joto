#!/usr/bin/env python



import datetime
import subprocess
from pathlib import Path
import sqlite3
import shutil
from wand.image import Image

import unittest

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import joto


class TestSQLiteDB(unittest.TestCase):

    def test_create_table(self):

        db_path = "test.db"
        table = '''test'''

        if os.path.isfile(db_path): 
            os.remove(db_path)
            print("First remove exiting db")

        sqlite_db = joto.SQLiteDB(db_path,table)
        sqlite_db.create_db_table()

        if os.path.isfile(db_path):
            result = True

        self.assertTrue(result) 

    def test_add_retrieve_data(self):

        db_path = "test.db"
        table = '''test'''

        if os.path.isfile(db_path): 
            os.remove(db_path)
            print("First remove exiting db")

        sqlite_db = joto.SQLiteDB(db_path,table)
        sqlite_db.create_db_table()
        sqlite_db.check_for_table()

        title = "2020-02-24_by_the_sea"
        date = "2020-02-24"
        text = "Swimming in the sea"
        image = "2020-02-24_by_the_sea.jpg"
        
        sqlite_db.add_joto_data(title, date, text, image)
        all_data = sqlite_db.retrieve_all_data_ordered_by_date()
        if all_data[0][4] == image:
            result = True
        
        self.assertTrue(result) 

    def test_compress_image(self):

        size_reduction_factor = 10 #%

        image = "2020-03-17_Sox.jpg"
        src_dir = "ingest_images/"
        dst_dir = "compressed_images/"
        achv_dir = "archived_images/"
        size = "1000x1000"

        original_image_size = int(os.stat(image)[6])

        #setup
        try:
            shutil.rmtree(src_dir)
            shutil.rmtree(dst_dir)
            shutil.rmtree(achv_dir)
        except: pass

        os.mkdir(src_dir) 
        os.mkdir(dst_dir) 
        os.mkdir(achv_dir) 
        shutil.copy(image,src_dir + image)

        images_manage = joto.ImagesManage(size,src_dir,dst_dir,achv_dir)
        images_manage.compress_image(image)

        compressed_image_size = int(os.stat(dst_dir + image)[6])

        if (compressed_image_size/original_image_size) < (size_reduction_factor/100):
            result = True

        self.assertTrue(result)
        



if __name__ == '__main__':
    unittest.main()
