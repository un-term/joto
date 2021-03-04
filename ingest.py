#!/usr/bin/python

import datetime
import os
import subprocess
from pathlib import Path
import sqlite3
import shutil
from wand.image import Image

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def insert_data_sql(title, date, text, image):
    try:
        sqliteConnection = sqlite3.connect('joto.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_insert_with_param = """INSERT INTO joto
                          (title, date, text, image) 
                          VALUES (?, ?, ?, ?);"""

        data_tuple = (title, date, text, image)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        print("Python Variables inserted successfully into joto table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def exportPhotoText(text,photo):
    pass

def write_to_file(file_name, text):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "w") as file_object:
        file_object.write(text)

ingest_dir = Path("ingest_images")

if ingest_dir.exists():
    for root, dirs, files in os.walk(ingest_dir): 
        for file in files:
            title = os.path.splitext(file)[0]
            date = title[:10]
            validate(date)
            print(title)        
            text = input("Text: ")
            # text = ""

            insert_data_sql(title,date,text,file)

            #compression 
            resize = "1000x1000" # ratio preserved in imagemagik
            src = "ingest_images/" + file
            dst = "images/compressed/" + file
            convert_OScommand = subprocess.run(["convert", "-resize", resize, src, dst], check=True)

            # Move image file to images/
            src = "ingest_images/" + file
            dst = "images/original"
            shutil.move(src,dst)

            # compress photo
            # with Image(filename="images/original/" + file) as img:
            #     img.resize(1000, 800)
            #     img.save(filename="images/compressed/" + file)

            # Export text to .text file
            dst = "text/"+title+".txt"
            write_to_file(dst,text)
            #copy file to images folder
            #export text to file



            

# handle return value
# feh and multiple photos on the same date

