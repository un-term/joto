#!/usr/bin/python

import datetime
import os
import subprocess
from pathlib import Path
import sqlite3
import shutil

# def photo_integrity_check():
    # try:
    #     sqliteConnection = sqlite3.connect('joto.db')
    #     cursor = sqliteConnection.cursor()
    #     print("Connected to SQLite")

    #     sqlite_select_query = """SELECT * from joto
    #                         ORDER BY date ASC;"""
    #     cursor.execute(sqlite_select_query)
    #     records = cursor.fetchall()

    #     ingest_dir = Path("images/compressed")

    #     for root, dirs, files in os.walk(ingest_dir)
    #         for file in files:
    #             found_file = False
    #             for row in records:
    #                 if row[4] == file:
    #                     print(file,"found")
    #                     found_file = True

    #             if found_file == False:
    #                 return False   

    #     cursor.close()

    # except sqlite3.Error as error:
    #     print("Failed to read data from sqlite table", error)
    # finally:
    #     if sqliteConnection:
    #         sqliteConnection.close()
    #         print("The SQLite connection is closed")
# print(photo_integrity_check())

# def printing(func):
#     def wrap(*args, **kwargs):
#         args = list(args)
#         print(args)
#         return func(*args, **kwargs)
#     return wrap

# @printing
# def my_add(a,b):
#     return a+b

# # breakpoint()
# my_add(1,2)


# defining a decorator
class Test():
    def hello_decorator(func):  
        
        # inner1 is a Wrapper function in   
        # which the argument is called  
       # inner function can access the outer local  
        # functions like in this case "func"  
        def inner1(self,*args, **kwargs):  
            print("Hello, this is before function execution")  
            # calling the actual function now  
            # inside the wrapper function.  
            func(self,*args, **kwargs)
        
            print("This is after function execution")  
                
        return inner1  
    
    
    # defining a function, to be called inside wrapper
    @hello_decorator
    def function_to_be_used(self,word):  
        print(f"This is inside the function: {word}")  
    
    
# passing 'function_to_be_used' inside the  
# decorator to control its behavior  
# function_to_be_used = hello_decorator(function_to_be_used)  
    
    
# calling the function
test = Test()
test.function_to_be_used("test")
# 

