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

    def test_all(self):
        print("------------------------------------------")
        print("Add new entry")
        print("------------------------------------------")

        image1 = "2021-04-21_parrots.jpg"
        image2 = "2021-01-02_fox.jpg"
        image3 = "2021-03-04_cow.jpg"
        image4 = "2020-11-10_giraffe.jpg"
        image5 = "2021-01-02_bird.jpg"
        html_template = "template.html"
        size = "1000x1000"

        if not os.path.exists("test_workspace"):
            os.makedirs("test_workspace")        
        # load config and setup objects
        if os.path.isfile("test_config.json"):
            json_config = joto.JsonConfig("test_config.json")
        else:
            raise Exception("config file required") 

        sqlite_db = joto.JotoSQLiteDB(json_config.sqlite_db_path)
        images_manage = joto.ImagesManage(json_config.image_size, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
        html = joto.HTML("./templates/output.html", json_config.html_output_path, json_config.compressed_image_dirpath)
        joto_obj = joto.Joto(sqlite_db, images_manage, html)

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()

        joto_obj.add_new_entry("2023-03-04", "This is a cow", "./test_data/2021-03-04_cow.jpg")
        joto_obj.create_content()
        joto_obj.write_content()

        joto_obj.add_new_entry("2023-05-26", "Giraffing around", "./test_data/2020-11-10_giraffe.jpg")
        joto_obj.create_content()
        joto_obj.write_content()

        joto_obj.add_new_entry("2023-07-26", "no image", "")
        joto_obj.create_content()
        joto_obj.write_content()

        # Scanning directory
        # joto_obj.scan_for_and_add_images_with_text(src_dir)
        # Test deleting - scan order dependent on filename - last fat_Sox
        # joto_obj.delete_entry(1)

        # text_input.get_input.return_value = "2020-02-12"
        # joto_obj.add_text_only()
        # joto_obj.delete_last_entry()

        # Test text for same date
        # text_input.get_input.return_value = "2020-02-12"
        # joto_obj.add_text_only()
        # text_input.get_input.return_value = "2020-02-12"
        # joto_obj.add_text_only()

        # Add image using path
        # joto_obj.add_image_from_path(img_path)

        # joto_obj.create_content()
        # joto_obj.write_content()

        # all_data = sqlite_db.retrieve_all_data_ordered_by_date()
        # result = False
        # if all_data[0][3] == image1: # first dated image
        #     result = True
        # joto_obj.scan_for_and_add_images_with_text()

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
