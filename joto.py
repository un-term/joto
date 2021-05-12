#!/usr/bin/env python

import sqlite3
import datetime
import os
from subprocess import Popen, PIPE
import sqlite3
import shutil
import sys
import getopt

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
                print("Successfully connected to: ", self.db)

                output = func(self, *args, **kwargs)

            except sqlite3.Error as error:
                print("Error while working with SQLite", error)
            finally:
                if self.connection:
                    self.connection.close()
                print("Sqlite connection is closed")
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
        print("SQLite table 'joto' created")

    @connect
    def add_joto_data(self, date, text, image):
        cursor = self.connection.cursor()

        sqlite_insert_with_param = '''INSERT INTO joto
                          (date, text, image)
                          VALUES (?, ?, ?);'''

        data_tuple = (date, text, image)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        self.connection.commit()
        cursor.close()

    @connect
    def retrieve_all_data_ordered_by_date(self):
        cursor = self.connection.cursor()

        sqlite_select_query = '''SELECT * from joto
                                ORDER BY date ASC;'''
        cursor.execute(sqlite_select_query)
        db_data = cursor.fetchall()
        cursor.close()
        return db_data

    def check_images_integrity(self):
        '''Check that images listed in db are also in images/compressed'''
        pass

    @connect
    def delete_last_row(self):
        '''Deletes last added row, not oldest'''
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
    def __init__(self,size, dst_dir, achv_dir):
        self.size = size  # compression size
        self.src_dir = None
        self.dst_dir = dst_dir
        self.achv_dir = achv_dir
        self.file_types = ["jpg","JPG","jpeg","JPEG","png","PNG"]
        self.target_size = 20  # %

    def check_req(self):
        count = 2
        if os.path.exists(self.dst_dir): count -= 1
        if os.path.exists(self.achv_dir): count -= 1
        if count == 0:
            return True
        else:
            return False

    def create_req(self):
        os.makedirs(self.dst_dir)
        os.makedirs(self.achv_dir)

    def delete_req(self):
        if os.path.exists(self.dst_dir): shutil.rmtree(self.dst_dir)
        if os.path.exists(self.achv_dir): shutil.rmtree(self.achv_dir)

    def delete(self, image):
        if not image == "None":
            print("Delete image: ", image)
            os.remove(self.dst_dir + image)
            os.remove(self.achv_dir + image)

    def compress_and_archive_image(self,name):
        src_filepath = self.src_dir + name
        dst_filepath = self.dst_dir + name
        achv_filepath = self.achv_dir + name

        self._compress_image(src_filepath,dst_filepath)
        if self._check_compression(src_filepath,dst_filepath):
            self._archive_original_image(src_filepath,achv_filepath)        
        else: raise Exception("Compression issue: could be low compression")

    def _compress_image(self,src_filepath,dst_filepath):
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
        check = False
        for ext in self.file_types:
            if name.endswith(ext):
                check = True
        if not check: raise Exception("Error: Incorrect file type")


class TextInput():

    def get_input(self):
        return input("Text: ")


class FormatContent():
    '''Create list with format content
       The following methods form a common interface'''

    def create_req(self):
        pass

    def check_req(self):
        pass

    def delete_req(self):
        pass

    def create_content(self):
        pass

    def write_content(self, content):
        pass


class Latex(FormatContent):
    def __init__(self,latex_dir):
        self.dir = latex_dir
        self.template_file = "template.tex"
        self.joto_file = "joto.tex"
        self.content = []

    def create_req(self):
        os.makedirs(self.dir)

    def check_req(self):
        count = 2
        if os.path.exists(self.dir): count -= 1
        if os.path.exists(self.template_file): count -= 1
        if count == 0: return True
        else: return False

    def delete_req(self):
        if os.path.exists(self.dir): shutil.rmtree(self.dir)

    def create_content(self, db_data):
        shutil.copyfile(self.template_file,self.joto_file)
        date = None
        switch_star = False
        for row in db_data:
            prev_date = date
            date = row[1]
            text = row[2]
            image = row[3]

            # Empty line and switch column
            if prev_date != None:
                if not switch_star:
                    self.snpt_switch_empty_line()
                elif switch_star:
                    self.snpt_switch_star_empty_line()
                switch_star = not switch_star

            # Text only
            if image == "None":
                self.snpt_just_text(date,text)
            else:
                # Multiple images for same date
                if prev_date == date:
                    self.snpt_image_without_date(image,text)
                # Image with text - normal
                else:
                    self.snpt_image_with_text(date,image,text)

        self.snpt_switch_empty_line()
        self.snpt_end()

    def write_content(self):
        append_multiple_lines_to_file(self.joto_file, self.content)
        self.latexmk()

    def snpt_image_with_text(self,date,image,text):
        self.content.extend([
           self._add_date(date),
           self._add_empty_line(),
           self._add_image(image),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_image_without_date(self,image,text):
        self.content.extend([
           self._add_image(image),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_just_text(self,date,text):
        self.content.extend([
           self._add_date(date),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_switch_empty_line(self):
        self.content.extend([
           self._add_switch(),
           self._add_empty_line()
        ])

    def snpt_switch_star_empty_line(self):
        self.content.extend([
           self._add_switch_star(),
           self._add_empty_line()
        ])

    def snpt_end(self):
        '''Already a list'''
        self.content.extend(self._add_end())

    def _add_date(self,date):
        return "\section*{" + date + "}"

    def _add_image(self,image):
        '''Image size restricted by max size option'''
        # return "\includegraphics[height=\columnwidth,keepaspectratio]{" + image + "}"
        return "\includegraphics[max size={\columnwidth}{\columnwidth}]{" + image + "}"

    def _add_text(self,text):
        return text

    def _add_switch(self):
        return "\switchcolumn"

    def _add_switch_star(self):
        return "\switchcolumn*"

    def _add_empty_line(self):
        # pass
        return ""

    def _add_end(self):
        return ["\end{paracol}","\end{document}"]

    def latexmk(self):
        p = Popen(["latexmk", "-pdf", "-jobname=latex/joto", "joto.tex"], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            print("Latexmk failed  %d %s %s" % (p.returncode, output, error))


class HTML():
    def __init__(self):
        self.template_file = "template.html"
        self.joto_file = "joto.html"
        self.image_dir = "images/compressed/"
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
        shutil.copyfile(self.template_file,self.joto_file)
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
                    self.snpt_empty_line()
                    self.snpt_text(text_list)
                    text_list.clear()
                    self.snpt_empty_line()
                    self.snpt_date(date)
                    self.snpt_image(image)
                    text_list.append(text)

        self.snpt_text(text_list)
        self.snpt_end()

    def write_content(self):
        append_multiple_lines_to_file(self.joto_file, self.content)

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


class Joto():
    def __init__(self, sqlite_db, images_manage, text_input, format):

        self.sqlite_db = sqlite_db
        self.images_manage = images_manage
        self.text_input = text_input
        self.format = format

    def check_req(self):
        '''Not to be used as part of other functions - manual intervention required'''
        if all([
            self.sqlite_db.check_req(),
            self.images_manage.check_req(),
            self.format.check_req()
            ]):
            print("Requirements met!")
        else: raise Exception("Requiements are NOT met")

    def create_req(self):
        self.sqlite_db.create_req()
        self.images_manage.create_req()
        self.format.create_req()
        print("db,table and paths created")

    def delete_req(self):
        self.sqlite_db.delete_req()
        self.images_manage.delete_req()
        self.format.delete_req()
        print("db and paths deleted")

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
        print("Date YYYY-MM-DD")
        date = self.text_input.get_input()
        self.validate(date)
        text = self.text_input.get_input()
        self.sqlite_db.add_joto_data(date,text,image="None")# db input order

    def scan_for_and_add_images_with_text(self,scan_path):
        self.images_manage.src_dir = scan_path
        for root, dirs, files in os.walk(self.images_manage.src_dir): 
            for file in files:
                self.images_manage.check_filetype(file)
                title,date = self.extract_attributes(file)
                print(title)
                text = self.text_input.get_input()
                self.images_manage.compress_and_archive_image(file)
                # Add to db after compressing image - if compression fail, not added to db
                self.sqlite_db.add_joto_data(date,text,file)# db input order

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


def main(argv):
    # Change to script directory
    # abspath = os.path.abspath(sys.argv[0])
    # dname = os.path.dirname(abspath)
    # os.chdir(dname)

    db_path = "joto.db"
    dst_dir = "images/compressed/"
    achv_dir = "images/original/"
    latex_dir = "latex/"
    size = "1000x1000"
    print(f"SQLite db path: {db_path}")

    sqlite_db = JotoSQLiteDB(db_path)
    images_manage = ImagesManage(size, dst_dir, achv_dir)
    text_input = TextInput()
    latex = Latex(latex_dir)
    html = HTML()

    # Specify format type here
    joto_obj = Joto(sqlite_db, images_manage, text_input, html)

    options, arguments = getopt.getopt(sys.argv[1:] , "" ,
        ["help","scan=", "text", "create-req", "delete-req","delete-entry=","delete-last-entry", "create-content"]) 

    for option, argument in options:
        if option == "--scan":
            if os.path.exists(argument):
                print("Scan: ", argument)
                joto_obj.check_req()
                joto_obj.scan_for_and_add_images_with_text(argument)
                joto_obj.create_content()
                joto_obj.write_content()
        elif option == "--text":
            joto_obj.check_req()
            joto_obj.add_text_only()
            joto_obj.create_content()
            joto_obj.write_content()
        elif option == "--create-content":
            joto_obj.create_content()
            joto_obj.write_content()
        elif option == "--create-req":
            joto_obj.create_req()
            joto_obj.check_req()
        elif option == "--delete-req":
            joto_obj.delete_req()
        elif option == "--delete-entry":
            joto_obj.delete_entry(argument)
        elif option == "--delete-last-entry":
            joto_obj.delete_last_entry()
        elif option == "--help":
            print("Options:","--scan","--text","--create-content","--create-req","--delete-req","--delete-last-entry")

 
if __name__ == "__main__":
   main(sys.argv[1:])
