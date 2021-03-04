#!/usr/bin/python

import datetime
import os
import subprocess
from pathlib import Path
import sqlite3
import shutil
from wand.image import Image

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

        for root, dirs, files in os.walk(ingest_dir)
            for file in files:
                found_file = False
                for row in records:
                    if row[4] == file:
                        print(file,"found")
                        found_file = True

                if found_file == False:
                    return False   

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

print(photo_integrity_check())