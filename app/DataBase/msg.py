import os.path
import sqlite3

DB = None
cursor = None
misc_path = "./app/Database/Msg/MSG0.db"
# misc_path = './Msg/Misc.db'
if os.path.exists(misc_path):
    DB = sqlite3.connect(misc_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()
