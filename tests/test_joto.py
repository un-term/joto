#!/usr/bin/env python

import datetime
import subprocess
from pathlib import Path
import sqlite3
import shutil

import unittest
from unittest.mock import Mock

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import joto


class TestSQLiteDB(unittest.TestCase):

    # def test_create_table(self):
    #     print("----------------------")
    #     print("Test creating db")
    #     print("----------------------")

    #     db_path = "test.db"

    #     if os.path.isfile(db_path): 
    #         os.remove(db_path)
    #         print("First remove exiting db")

    #     sqlite_db = joto.JotoSQLiteDB(db_path)
    #     sqlite_db.create_db_table()

    #     if os.path.isfile(db_path):
    #         result = True

    #     self.assertTrue(result) 

    # def test_add_and_get_data(self):
    #     print("----------------------")
    #     print("Test getting data from table db")
    #     print("----------------------")

    #     db_path = "test.db"

    #     if os.path.isfile(db_path): 
    #         os.remove(db_path)
    #         print("First remove existing db")

    #     sqlite_db = joto.JotoSQLiteDB(db_path)
    #     sqlite_db.create_db_table()
    #     sqlite_db.check_for_table()

    #     title = "2020-02-24_by_the_sea"
    #     date = "2020-02-24"
    #     text = "Swimming in the sea"
    #     image = "2020-02-24_by_the_sea.jpg"
        
    #     sqlite_db.add_joto_data(title, date, text, image)
    #     all_data = sqlite_db.retrieve_all_data_ordered_by_date()
    #     if all_data[0][4] == image:
    #         result = True
        
    #     self.assertTrue(result) 

    # def test_compress_image(self):
    #     print("----------------------")
    #     print("Test image compression")
    #     print("----------------------")

    #     image = "2020-03-17_Sox.jpg"
    #     size = "1000x1000"
    #     size_reduction_factor = 10 #%

    #     #setup
    #     #--------------------------------------------------
    #     db_path = "test.db"
    #     src_dir = "ingest_images/"
    #     dst_dir = "images/compressed/"
    #     achv_dir = "images/original/"

    #     if os.path.exists(db_path): os.remove(db_path)
    #     if os.path.exists(src_dir): shutil.rmtree(src_dir)
    #     if os.path.exists(dst_dir): shutil.rmtree(dst_dir)
    #     if os.path.exists(achv_dir): shutil.rmtree(achv_dir)

    #     os.mkdir(src_dir) 
    #     os.makedirs(dst_dir) 
    #     os.makedirs(achv_dir) 
    #     shutil.copy(image,src_dir + image)
    #     #--------------------------------------------------

    #     original_image_size = int(os.stat(image)[6])

    #     images_manage = joto.ImagesManage(size,src_dir,dst_dir,achv_dir)
    #     images_manage.compress_and_archive_image(image)

    #     compressed_image_size = int(os.stat(dst_dir + image)[6])

    #     if (compressed_image_size/original_image_size) < (size_reduction_factor/100):
    #         result = True

    #     self.assertTrue(result)

    # def test_create_requirements(self):
    #     print("------------------------------------------")
    #     print("Integration test: creating paths, db, table")
    #     print("------------------------------------------")

    #     image = "2020-03-17_Sox.jpg"
    #     size = "1000x1000"

    #     #setup
    #     #--------------------------------------------------
    #     db_path = "test.db"
    #     src_dir = "ingest_images/"
    #     dst_dir = "images/compressed/"
    #     achv_dir = "images/original/"
    #     latex_dir = "latex/"

    #     if os.path.exists(db_path): os.remove(db_path)
    #     if os.path.exists(src_dir): shutil.rmtree(src_dir)
    #     if os.path.exists(dst_dir): shutil.rmtree(dst_dir)
    #     if os.path.exists(achv_dir): shutil.rmtree(achv_dir)
    #     if os.path.exists(latex_dir): shutil.rmtree(latex_dir)

    #     # shutil.copy(image,src_dir + image)
    #     #--------------------------------------------------

    #     text_input = Mock()

    #     sqlite_db = joto.JotoSQLiteDB(db_path)
    #     images_manage = joto.ImagesManage(size, src_dir, dst_dir, achv_dir)
    #     text_input = joto.TextInput()
    #     latex = joto.Latex(latex_dir)
    #     joto_obj = joto.Joto(sqlite_db,images_manage,text_input,latex)

    #     joto_obj.create_all_requirements()
    #     joto_obj.check_requirements()
    #     # joto_obj.scan_for_and_add_images_with_text()

    #     self.assertTrue(True)

    def test_all(self):
        print("------------------------------------------")
        print("Integration test: adding image")
        print("------------------------------------------")

        image1 = "2021-04-21_parrots.jpg"
        image2 = "2021-01-02_fox.jpg"
        image3 = "2021-03-04_cow.jpg"
        image4 = "2020-11-10_giraffe.jpg"
        image5 = "2021-01-02_bird.jpg"
        not_image ="test"
        latex_template = "template.tex"
        html_template = "template.html"
        size = "1000x1000"

        #setup
        #--------------------------------------------------
        db_path = "test.db"
        src_dir = "ingest_images/"
        dst_dir = "images/compressed/"
        achv_dir = "images/original/"
        latex_dir = "latex/"

        # Copy required test files 
        #--------------------------------------------------
        shutil.copy(image1,src_dir + image1)  # deleted as part of test
        shutil.copy(image2,src_dir + image2)
        shutil.copy(image3,src_dir + image3)
        shutil.copy(image4,src_dir + image4)
        shutil.copy(image5,src_dir + image5)
        shutil.copy(not_image,src_dir + not_image)
        shutil.copy("../" + latex_template, latex_template)
        shutil.copy("../" + html_template, html_template)

        text_input = Mock()
        text_input.get_input.return_value = "Lorem ispum etc"

        sqlite_db = joto.JotoSQLiteDB(db_path)
        images_manage = joto.ImagesManage(size, dst_dir, achv_dir)
        # text_input = joto.TextInput()
        latex = joto.Latex(latex_dir)
        html = joto.HTML()

        joto_obj = joto.Joto(sqlite_db, images_manage, text_input, html)
        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()

        joto_obj.scan_for_and_add_images_with_text(src_dir)
        # Test deleting - scan order dependent on filename - last fat_Sox
        joto_obj.delete_entry(1)

        text_input.get_input.return_value = "2020-02-12"
        joto_obj.add_text_only()
        joto_obj.delete_last_entry()

        # Test text for same date
        text_input.get_input.return_value = "2020-02-12"
        joto_obj.add_text_only()
        text_input.get_input.return_value = "2020-02-12"
        joto_obj.add_text_only()

        joto_obj.create_content()
        joto_obj.write_content()

        # all_data = sqlite_db.retrieve_all_data_ordered_by_date()
        # result = False
        # if all_data[0][3] == image1: # first dated image
        #     result = True
        # joto_obj.scan_for_and_add_images_with_text()

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
