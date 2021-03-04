#!/usr/bin/python

import sqlite3
import shutil
import subprocess
from pathlib import Path

def photo_integrity_check():
    try:
        sqliteConnection = sqlite3.connect('joto.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from joto
                            ORDER BY date ASC;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()

        ingest_dir = Path("images/compressed")

        for root, dirs, files in os.walk(ingest_dir):
            for file in files:
                found_file = False
                for row in records:
                    if row[4] == file:
                        print(found)
                        found_file = True

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")


    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def read_data_sql():
    try:
        sqliteConnection = sqlite3.connect('joto.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from joto
                            ORDER BY date ASC;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        print("Printing each row")
        print(records)
        cursor.close()
        return records
        # for row in records:
        #     # id, title, date, text, image
        #     print()
        #     return row[0],row[1],row[2],row[3],row[4]
            # print("\n")


    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def append_multiple_lines(file_name, lines_to_append):
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        appendEOL = False
        # Move read cursor to the start of file.
        file_object.seek(0)
        # Check if file is not empty
        data = file_object.read(100)
        if len(data) > 0:
            appendEOL = True
        # Iterate over each string in the list
        for line in lines_to_append:
            # If file is not empty then append '\n' before first line for
            # other lines always append '\n' before appending line
            if appendEOL == True:
                file_object.write("\n")
            else:
                appendEOL = True
            # Append element at the end of file
            file_object.write(line)


class Latex():
    def __init__(self):
        self.content = []

    def add_date(self,date):
        return "\section*{" + date + "}"

    def add_image(self,file):
        # return "\includegraphics[height=\columnwidth,keepaspectratio]{" + file + "}"
        return "\includegraphics[max size={\columnwidth}{\columnwidth}]{" + file + "}"

    def add_swtich(self):
        return "\switchcolumn"



# main

src = "template.tex"
dst = "joto.tex"
shutil.copyfile(src,dst)

db_data = read_data_sql()

latex = Latex()
prev_date = None
for row in db_data:
    date = row[2]
    if not prev_date == date:
        latex.content.append(latex.add_date(date))
    image = row[4]
    latex.content.append(latex.add_image(image))
    latex.content.append("")
    text = row[3]
    latex.content.append(text)
    latex.content.append(latex.add_swtich())
    latex.content.append("")

    prev_date = date

# ends
latex.content.append("\end{paracol}")
latex.content.append("\end{document}")

print("Copy db contents to joto.tex")

append_multiple_lines("joto.tex",latex.content)

convert_OScommand = subprocess.run(["latexmk", "-pdf", "-jobname=latex/joto", "joto.tex"], check=True)


# print(latex.content)
# for row in latex.content:
#     print(row)




# append_new_line()
