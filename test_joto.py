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

def check_string(file_path, stringFind):
    with open(file_path, 'r') as file:
        content = file.read()
        if stringFind in content:
            return True
        else:
            return False

class TestSQLiteDB(unittest.TestCase):

    def test_add_new_entry1(self):
        print("------------------------------------------")
        print("Add new entry:date, image, text")
        print("------------------------------------------")

        if not os.path.exists("test_workspace"):
            os.makedirs("test_workspace")        
        # load config and setup objects
        if os.path.isfile("test_config.json"):
            json_config = joto.JsonConfig("test_config.json")
        else:
            raise Exception("config file equired") 

        sqlite_db = joto.JotoSQLiteDB(json_config.sqlite_db_path)
        images_manage = joto.ImagesManage(json_config.image_size, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
        html = joto.HTML("./templates/output.html", json_config.html_output_path, json_config.compressed_image_dirpath)
        joto_obj = joto.Joto(sqlite_db, images_manage, html)

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()

        joto_obj.add_new_entry("2021-03-04", "This is a cow", "./test_data/2021-03-04_cow.jpg")
        joto_obj.create_content()
        joto_obj.write_content()

        count = 0
        if check_string("test_workspace/joto.html",'<h1>2021-03-04</h1>'):
            count += 1
        if check_string("test_workspace/joto.html",'<img src="test_workspace/images/compressed/2021-03-04_cow.jpg">'):
            count += 1
        if check_string("test_workspace/joto.html",'<p>This is a cow</p>'):
            count += 1
            
        self.assertEqual(3, count)


    def test_add_new_entry2(self):
        print("")
        print("------------------------------------------")
        print("Add new entry:date, text, no image")
        print("------------------------------------------")

        if not os.path.exists("test_workspace"):
            os.makedirs("test_workspace")        
        # load config and setup objects
        if os.path.isfile("test_config.json"):
            json_config = joto.JsonConfig("test_config.json")
        else:
            raise Exception("config file equired") 

        sqlite_db = joto.JotoSQLiteDB(json_config.sqlite_db_path)
        images_manage = joto.ImagesManage(json_config.image_size, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
        html = joto.HTML("./templates/output.html", json_config.html_output_path, json_config.compressed_image_dirpath)
        joto_obj = joto.Joto(sqlite_db, images_manage, html)

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()

        joto_obj.add_new_entry("2021-01-02", "", "./test_data/2021-01-02_fox.jpg")
        joto_obj.create_content()
        joto_obj.write_content()

        count = 0
        if check_string("test_workspace/joto.html",'check_string("test_workspace/joto.html","<h1>2021-01-02</h1>")'):
            count += 1
        if check_string("test_workspace/joto.html",'<img src="test_workspace/images/compressed/2021-01-02_fox.jpg">'):
            count += 1
        if check_string("test_workspace/joto.html",'<p></p>'):
            count += 1
            
        self.assertEqual(2, count)


if __name__ == '__main__':
    unittest.main()
