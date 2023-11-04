#!/usr/bin/env python

import sqlite3
import datetime
import os
from subprocess import Popen, PIPE
import shutil
import sys
import getopt
import json

def append_multiple_lines_to_file(file_name, lines_to_append):
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        appendEOL = False
        # Move read cursor to the start of file.
        file_object.seek(0)
        # Check if file is not empty
        data = file_object.read(100)
        if len(data) > 0:
            appendEOL = True
        for line in lines_to_append:
            # If file is not empty then append '\n' before first line for
            # other lines always append '\n' before appending line
            if appendEOL is True:
                file_object.write("\n")
            else:
                appendEOL = True
            # Append element at the end of file
            file_object.write(line)


class JotoSQLiteDB():
    '''Performs fixed sql operations on joto table'''
    def __init__(self, db_path):
        self.db = db_path
        self.connection = None

    def connect(func):
        '''Decorator. func wrapped into 'wrap' and new 'wrap' returned'''
        def wrap(self,*args, **kwargs):
            output = None
            try:
                self.connection = sqlite3.connect(self.db)
                print("DB: Connected to: ", self.db)

                output = func(self, *args, **kwargs)

            except sqlite3.Error as error:
                print("ERROR: DB connection", error)
            finally:
                if self.connection:
                    self.connection.close()
            return output

        return wrap

    def check_req(self):
        if os.path.exists(self.db) and self._check_for_table():
            return True
        else:
            return False

    def create_req(self):
        '''db created when table created'''
        self._create_db_table()

    def delete_req(self):
        if os.path.exists(self.db):
            os.remove(self.db)

    @connect
    def _check_for_table(self):
        print("DB: Check table exists")
        cursor = self.connection.cursor()
        sqlite_query = ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='joto'; '''
        cursor.execute(sqlite_query)

        table_exists = False
        if cursor.fetchone()[0] == 1:
            table_exists = True
        cursor.close()
        return table_exists

    @connect
    def _create_db_table(self):
        print("DB: Create db table")
        cursor = self.connection.cursor()
        sqlite_create_table_query = '''CREATE TABLE joto (
                                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                                date  TEXT NOT NULL,
                                text  TEXT NOT NULL,
                                image TEXT NOT NULL
                            );'''

        cursor.execute(sqlite_create_table_query)
        self.connection.commit()
        cursor.close()

    @connect
    def add_joto_data(self, date, text, image):
        print("DB: Add data:")
        print("    date: ", date)
        print("    text: ", text)
        print("    image: ", image)
        cursor = self.connection.cursor()

        sqlite_insert_with_param = '''INSERT INTO joto
                          (date, text, image)
                          VALUES (?, ?, ?);'''

        data_tuple = (date, text, image)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        self.connection.commit()
        cursor.close()
        return True

    @connect
    def retrieve_all_data_ordered_by_date(self):
        print("DB: Get data ordered by date")
        cursor = self.connection.cursor()

        sqlite_select_query = '''SELECT * from joto
                                ORDER BY date DESC;'''
        cursor.execute(sqlite_select_query)
        db_data = cursor.fetchall()
        cursor.close()
        return db_data
    
    @connect
    def get_last_row(self):
        '''Get last row added, not oldest'''
        print("DB: get last row added")
        cursor = self.connection.cursor()

        # Get last image filename for deleting
        sql_query = """select * from joto where id = (SELECT MAX(id) FROM joto);"""
        cursor.execute(sql_query)
        lastrow = cursor.fetchall()
        return lastrow[0]   

    def check_images_integrity(self):
        '''Check that images listed in db are also in images/compressed'''
        pass

    @connect
    def delete_last_row(self):
        '''Delete last row added, not oldest'''
        print("DB: Delete last row added")
        cursor = self.connection.cursor()

        # Get last image filename for deleting
        sql_query = """select * from joto where id = (SELECT MAX(id) FROM joto);"""
        cursor.execute(sql_query)
        records = cursor.fetchall()
        print("Delete db row: ", records)
        image = records[0][3]

        sqlite_query = '''DELETE FROM joto
                          WHERE id = (SELECT MAX(id) FROM joto);'''
        cursor.execute(sqlite_query)
        self.connection.commit()
        cursor.close()

        return image


    @connect
    def delete_row(self, id):
        '''Delete row with id'''
        print("DB: Delete row :", id)
        cursor = self.connection.cursor()

        sql_query = """select * from joto where id = ?"""
        cursor.execute(sql_query, (id,))
        records = cursor.fetchall()
        image = records[0][3]

        print(f"Delete db row {id}")
        sql_query = '''DELETE FROM joto
                          WHERE id = ?;'''
        cursor.execute(sql_query, (id,))
        self.connection.commit()

        cursor.close()
        return image


class ImagesManage():
    def __init__(self,size,upld_dir, dst_dir, achv_dir):
        self.size = size  # compression size
        self.upld_dir = upld_dir
        self.dst_dir = dst_dir
        self.achv_dir = achv_dir
        self.file_types = ["jpg","JPG","jpeg","JPEG","png","PNG"]
        self.target_size = 20  # %

    def get_upld_dir(self):
        return self.upld_dir

    def check_req(self):
        count = 3
        if os.path.exists(self.upld_dir): count -= 1
        if os.path.exists(self.dst_dir): count -= 1
        if os.path.exists(self.achv_dir): count -= 1
        if count == 0:
            return True
        else:
            return False

    def create_req(self):
        os.makedirs(self.upld_dir)
        os.makedirs(self.dst_dir)
        os.makedirs(self.achv_dir)

    def delete_req(self):
        if os.path.exists(self.upld_dir): shutil.rmtree(self.upld_dir)
        if os.path.exists(self.dst_dir): shutil.rmtree(self.dst_dir)
        if os.path.exists(self.achv_dir): shutil.rmtree(self.achv_dir)

    def delete(self, image):
        print("IM: Delete image :", image)
        if not image == "None":
            print("Delete image: ", image)
            os.remove(self.dst_dir + image)
            os.remove(self.achv_dir + image)

    def compress_image(self, image_filename, image_path):
        print("IM: Compress image :", image_filename)
        src_filepath = image_path
        dst_filepath = self.dst_dir + image_filename
        achv_filepath = self.achv_dir + image_filename

        self._compress_with_imagemagick(src_filepath,dst_filepath)
        if self._check_compression(src_filepath,dst_filepath):
            return True        
        else: 
            raise Exception("Compression issue: could be low compression")
            return False

    def archive_image_move(self, image_filename, image_path):
        src_filepath = image_path
        achv_filepath = self.achv_dir + image_filename
        shutil.move(src_filepath, achv_filepath)

    def archive_image_copy(self, image_filename, image_path):
        print("IM: Archive original image:", image_filename)
        src_filepath = image_path
        achv_filepath = self.achv_dir + image_filename
        shutil.copyfile(src_filepath, achv_filepath)

    def _compress_with_imagemagick(self,src_filepath,dst_filepath):
        '''https://stackoverflow.com/questions/24849998/how-to-catch-exception-output-from-python-subprocess-check-output'''
        p = Popen(["convert", "-resize", self.size, src_filepath,"-auto-orient", dst_filepath], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            print("Image Magik failed %d %s %s" % (p.returncode, output, error))

    def _check_compression(self,src_filepath,dst_filepath):
        if os.path.exists(dst_filepath):
            return True
        else:
            return False

    def _check_compression_size(self,src_filepath,dst_filepath):
        original_image_size = int(os.stat(src_filepath)[6])
        compressed_image_size = int(os.stat(dst_filepath)[6])
        # if (compressed_image_size/original_image_size) < (self.target_size/100):
        if compressed_image_size < 800000:
            return True
        else:
            return False

    def _archive_original_image(self, src_filepath, achv_filepath):
            shutil.move(src_filepath, achv_filepath)

    def check_filetype(self,name):
        for ext in self.file_types:
            if name.endswith(ext):
                return True
        print("IM ERROR: Incorrect image filetype")
        return False

class TextInput():

    def get_input(self):
        return input("Text: ")

class HTML():
    def __init__(self, template_file, output_html_file, image_dir):
        self.template_file = template_file
        self.output_html_file = output_html_file
        self.image_dir = image_dir
        self.content = []

    def create_req(self):
        pass

    def check_req(self):
        if os.path.exists(self.template_file):
            return True
        else:
            return False

    def delete_req(self):
        pass

    def create_content(self, db_data):
        print("HTML: Create html")
        shutil.copyfile(self.template_file,self.output_html_file)
        date = None
        text_list = []
        for row in db_data:
            prev_date = date
            date = row[1]
            text = row[2]
            image = row[3]

            if prev_date is None:
                self.snpt_empty_line()
                self.snpt_date(date)
                text_list.append(text)
                if image != "None":
                    self.snpt_image(image)

            else:
                if date == prev_date:
                    if image != "None":
                        self.snpt_image(image)
                        text_list.append(text)
                    else:
                        text_list.append(text)
                else:
                    self.snpt_empty_line()
                    self.snpt_text(text_list)
                    text_list.clear()
                    self.snpt_empty_line()
                    self.snpt_date(date)
                    if image != "None":
                        self.snpt_image(image)
                    text_list.append(text)

        self.snpt_text(text_list)
        self.snpt_end()

    def write_content(self):
        append_multiple_lines_to_file(self.output_html_file, self.content)

    def snpt_date(self, date):
        self.content.append(
           self._add_date(date)
        )

    def snpt_image(self, image):
        image_filepath = '"' + self.image_dir + image + '"'
        self.content.append(
           self._add_image(image_filepath)
        )

    def snpt_text(self, text_list):
        for line in text_list:
            self.content.append(
                self._add_text(line)
            )

    def snpt_empty_line(self):
        self.content.append(
           self._add_empty_line()
        )

    def snpt_end(self):
        '''Already a list'''
        self.content.extend(self._add_end())

    def _add_date(self,date):
        return "<h1>" + date + "</h1>"

    def _add_image(self,image):
        return "<img src=" + image + ">"  # alt text not added

    def _add_text(self,text):
        return "<p>" + text + "</p>"

    def _add_empty_line(self):
        return ""

    def _add_end(self):
        return ["</body>","</html>"]

class JsonConfig():
    def __init__(self, config_path):
        self.config_path = config_path
        self.sqlite_db_path = None
        self.upload_image_dirpath = None
        self.original_image_dirpath = None
        self.compressed_image_dirpath = None
        self.image_size = None
        self.html_output_path = None
        self.set_config_values()

    def set_config_values(self):
        with open(self.config_path, "r") as read_file:
            data = json.load(read_file)
            self.sqlite_db_path = data["sqlite_db_path"]
            self.upload_image_dirpath = data["upload_image_dirpath"]
            self.original_image_dirpath = data["original_image_dirpath"]
            self.compressed_image_dirpath = data["compressed_image_dirpath"]
            self.image_size = data["image_size"]
            self.html_output_path = data["html_output_path"]
            
class Joto():
    def __init__(self, sqlite_db, images_manage, format):

        self.sqlite_db = sqlite_db
        self.images_manage = images_manage
        self.format = format

    def check_req(self):
        '''Not to be used as part of other functions - manual intervention required'''
        if not self.sqlite_db.check_req(): raise Exception("sqlite requirements are not met")
        if not self.images_manage.check_req(): raise Exception("images_manage requirements are not met")
        if not self.format.check_req(): raise Exception("format requirements are not met")

    def create_req(self):
        self.sqlite_db.create_req()
        self.images_manage.create_req()
        self.format.create_req()

    def delete_req(self):
        self.sqlite_db.delete_req()
        self.images_manage.delete_req()
        self.format.delete_req()

    def check_date_format(self, date_text):
        try: 
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        # except ValueError:
        #     raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        except:
            print("Incorrect data format, should be YYYY-MM-DD")
            return False

    def extract_attributes(self, file):
        title = os.path.splitext(file)[0]
        date = title[:10]
        self.validate(date)
        return title,date

    def extract_filename(self, filename):
        return os.path.basename(filename)
    
    def add_new_entry(self, date, text, image_path):
        if not self.check_date_format(date): 
            return False

        if not text:
            text = ""
            
        if image_path:
            if self.images_manage.check_filetype(image_path):
                image_filename = self.extract_filename(image_path)
                if self.images_manage.compress_image(image_filename, image_path):
                    self.images_manage.archive_image_copy(image_filename, image_path)
                    # Add to db after compressing image - if compression fail, not added to db
                else:
                    return False
            else:
                return False
        else:
            image_filename = "None"


        if self.sqlite_db.add_joto_data(date,text,image_filename): # db input order
            return True # Return statements used for testing, test false statement to check checks pickup errors
        else: 
            return False
        
    def delete_last_entry(self):
        image = self.sqlite_db.delete_last_row()
        self.images_manage.delete(image)

    def delete_entry(self, id):
        id = int(id)
        image = self.sqlite_db.delete_row(id)
        self.images_manage.delete(image)

    def create_content(self):
        db_data = self.sqlite_db.retrieve_all_data_ordered_by_date()
        self.format.create_content(db_data)

    def write_content(self):
        self.format.write_content()
