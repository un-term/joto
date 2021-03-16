#!/usr/bin/env python

import sqlite3
import datetime
import os
import subprocess
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
                    print("Total Rows affected since the database connection was opened: ",self.connection.total_changes)
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
        if os.path.exists(self.db): os.remove(self.db)


    @connect
    # def check_for_table(self,connection):
    def _check_for_table(self):
        cursor = self.connection.cursor()
        sqlite_query = ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='joto'; '''
        cursor.execute(sqlite_query)
        if cursor.fetchone()[0] == 1: return True
        elif cursor.fetchone()[0] == 0: return False
        cursor.close()

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
        print("SQLite table created")

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
        return cursor.fetchall()
        cursor.close()

    def check_images_integrity(self):
        '''Check that images listed in db are also in images/compressed'''
        pass

    def remove_last_row():
        pass


class ImagesManage():
    def __init__(self,size, src_dir, dst_dir, achv_dir):
        # self.compression_size = "1000x1000"
        # self.src_dir = "ingest_images/"
        # self.dst_dir = "images/compressed/"
        self.size = size  # compression size
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.achv_dir = achv_dir
        self.file_types = ["jpg","JPG","jpeg","JPEG","png","PNG"]
        self.target_size = 20  #%


    def check_req(self):
        count = 3
        if os.path.exists(self.src_dir): count -= 1
        if os.path.exists(self.dst_dir): count -= 1
        if os.path.exists(self.achv_dir): count -= 1
        if count == 0: return True
        else: return False

    def create_req(self):
        os.makedirs(self.src_dir)
        os.makedirs(self.dst_dir)
        os.makedirs(self.achv_dir)

    def delete_req(self):
        if os.path.exists(self.src_dir): shutil.rmtree(self.src_dir)
        if os.path.exists(self.dst_dir): shutil.rmtree(self.dst_dir)
        if os.path.exists(self.achv_dir): shutil.rmtree(self.achv_dir)

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
        except: print("External Image Magik convert failed")

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


class Latex():
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

    def copy_template(self):
        shutil.copyfile(self.template_file,self.joto_file)

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

    def snpt_just_text(self,text):
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

    def append_content_to_latex_file(self):
        append_multiple_lines_to_file(self.joto_file,self.content)

    def latexmk(self):
        try: subprocess.run(["latexmk", "-pdf", "-jobname=latex/joto", "joto.tex"], check=True)
        except: print("Latexmk failed")


class Joto():
    def __init__(self, sqlite_db, images_manage, text_input, latex):

        self.sqlite_db = sqlite_db
        self.images_manage = images_manage
        self.text_input = text_input
        self.latex = latex

    def check_req(self):
        '''Not to be used as part of other functions - manual intervention required'''
        if all([
            self.sqlite_db.check_req(),
            self.images_manage.check_req(),
            self.latex.check_req()
            ]):
            print("Requirements met!")
        else: raise Exception("Requiements are NOT met")

    def create_req(self):
        self.sqlite_db.create_req()
        self.images_manage.create_req()
        self.latex.create_req()
        print("db,table and paths created")

    def delete_req(self):
        self.sqlite_db.delete_req()
        self.images_manage.delete_req()
        self.latex.delete_req()
        print("db and paths deleted")
        # if os.path.exists(self.sqlite_db.db): os.remove(self.sqlite_db.db)
        # if os.path.exists(self.images_manage.src_dir): shutil.rmtree(self.images_manage.src_dir)
        # if os.path.exists(self.images_manage.dst_dir): shutil.rmtree(self.images_manage.dst_dir)
        # if os.path.exists(self.images_manage.achv_dir): shutil.rmtree(self.images_manage.achv_dir)
        # if os.path.exists(self.latex.dir): shutil.rmtree(self.latex.dir)


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

    def export_text(path):
        pass

    def add_text_only(self):
        print("Date YYYY-MM-DD")
        date = self.text_input.get_input()
        self.validate(date)
        print("Text")
        text = self.text_input.get_input()
        image = "None"
        self.sqlite_db.add_joto_data(date,text,file)# db input order

    def scan_for_and_add_images_with_text(self):
        for root, dirs, files in os.walk(self.images_manage.src_dir): 
            for file in files:
                self.images_manage.check_filetype(file)
                title,date = self.extract_attributes(file)
                print(title)
                text = self.text_input.get_input()
                self.sqlite_db.add_joto_data(date,text,file)# db input order

                self.images_manage.compress_and_archive_image(file)

    def generate_latex(self):
        self.latex.copy_template()
        db_data = self.sqlite_db.retrieve_all_data_ordered_by_date()
        date = None
        switch_star = False
        for row in db_data:
            prev_date = date
            date = row[1]
            text = row[2]
            image = row[3]

            # if prev_date != date and prev_date != None:
            if prev_date != None:
                if not switch_star:
                    self.latex.snpt_switch_empty_line()
                elif switch_star:
                    self.latex.snpt_switch_star_empty_line()
                switch_star = not switch_star
            if prev_date == date:
                self.latex.snpt_image_without_date(image,text)
            elif prev_date != date:
                if image == "":
                    self.latex.snpt_just_text(date,text)
                else:
                    self.latex.snpt_image_with_text(date,image,text)

        self.latex.snpt_switch_empty_line()
        self.latex.snpt_end()

        self.latex.append_content_to_latex_file()
        self.latex.latexmk()


def main(argv):
    db_path = "joto.db"
    src_dir = "ingest_images/"
    dst_dir = "images/compressed/"
    achv_dir = "images/original/"
    latex_dir = "latex/"
    size = "1000x1000"
    print(f"SQLite db path: {db_path}")

    sqlite_db = JotoSQLiteDB(db_path)
    images_manage = ImagesManage(size, dst_dir, achv_dir)
    text_input = TextInput()
    latex = Latex(latex_dir)
    joto_obj = Joto(sqlite_db,images_manage,text_input,latex)

    try:
        opts, args = getopt.getopt(argv)
    except getopt.GetoptError:
        print('Incorrect input format!')
        sys.exit(2)

    if args[0] == "create_req":
        joto_obj.create_req()
        joto_obj.check_req()
    if args[0] == "delete_req":
        joto_obj.delete_req()
    elif args[0] == "text":
        joto_obj.check_req()
        joto_obj.add_text_only()
        joto_obj.generate_latex()
    elif args[0] == "scan":
        joto_obj.check_req()
        joto_obj.scan_for_and_add_images_with_text()
        joto_obj.generate_latex()
    else: print("Choose option: scan text export create_all_requirements")

 
if __name__ == "__main__":
   main(sys.argv[1:])
