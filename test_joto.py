#!/usr/bin/env python

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


# Setup
# ------------------------------------------------------------------------------
if not os.path.exists("test_workspace"):
    os.makedirs("test_workspace")        
# load config and setup objects
if os.path.isfile("test_config.json"):
    json_config = joto.JsonConfig("test_config.json")
else:
    print("Missing config file")
    exit() 

sqlite_db = joto.JotoSQLiteDB(json_config.sqlite_db_path)
images_manage = joto.ImagesManage(json_config.image_size, json_config.upload_image_dirpath, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
html = joto.HTML("./templates/output.html", json_config.html_output_path, json_config.compressed_image_dirpath)
joto_obj = joto.Joto(sqlite_db, images_manage, html)

# ------------------------------------------------------------------------------
class TestSQLiteDB(unittest.TestCase):

    def test_add_new_entry1(self):
        print("------------------------------------------")
        print("TEST 1")
        print("HTML Test")
        print("Add new entry:date, image, text")
        print("------------------------------------------")

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()
        joto_obj.copy_test_data()

        joto_obj.add_new_entry("2021-03-04", "This is a cow", "2021-03-04_cow.jpg")
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
        print("\n")
        print("------------------------------------------")
        print("TEST 2")
        print("DB test")
        print("No text, only image")
        print("------------------------------------------")

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()
        joto_obj.copy_test_data()

        count = 0
        # Check entry create successfully
        if joto_obj.add_new_entry("2021-01-02", "", "2021-01-02_fox.jpg"):
            count += 1

        # Check db contains correct data
        last_db_row = sqlite_db.get_last_row()
        print("Last db row: ", last_db_row)
        if last_db_row[1] == "2021-01-02":
            count += 1
        if last_db_row[2] == "":
            count += 1
        if last_db_row[3] == "2021-01-02_fox.jpg":
            count += 1
          
        self.assertEqual(4, count)

    def test_add_new_entry3(self):
        print("\n")
        print("------------------------------------------")
        print("TEST 3")
        print("DB test")
        print("No image, text only")
        print("------------------------------------------")

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()
        joto_obj.copy_test_data()

        count = 0
        # Check entry create successfully
        if joto_obj.add_new_entry("2022-03-02", "An interesting day", ""):
            count += 1

        # Check db contains correct data
        last_db_row = sqlite_db.get_last_row()
        print("Last db row: ", last_db_row)
        if last_db_row[1] == "2022-03-02":
            count += 1
        if last_db_row[2] == "An interesting day":
            count += 1
        if last_db_row[3] == "None":
            count += 1
          
        self.assertEqual(4, count)

    def test_add_new_entry4(self):
        print("\n")
        print("------------------------------------------")
        print("TEST 4")
        print("Input test")
        print("Wrong date format")
        print("------------------------------------------")

        joto_obj.delete_req()
        joto_obj.create_req()
        joto_obj.check_req()
        joto_obj.copy_test_data()

        count = 0
        # Check entry create successfully
        if not joto_obj.add_new_entry("2022-0302", "An interesting day", ""):
            count += 1
        # Also check if there is a database entry
        self.assertEqual(1, count)
       

    #tests
    # 5 missing image file
    # 6 html tests
    # 7 flask tests? connection check


if __name__ == '__main__':
    unittest.main()
