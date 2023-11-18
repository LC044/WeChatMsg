import os.path
import sqlite3
import threading

lock = threading.Lock()
DB = None
cursor = None
micromsg_path = "./app/Database/Msg/MicroMsg.db"
if os.path.exists(micromsg_path):
    DB = sqlite3.connect(micromsg_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(micromsg_path):
            DB = sqlite3.connect(micromsg_path, check_same_thread=False)
            # '''创建游标'''
            cursor = DB.cursor()


def is_database_exist():
    return os.path.exists(micromsg_path)


def get_contact():
    try:
        lock.acquire(True)
        sql = '''select UserName,Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl.bigHeadImgUrl
              from Contact inner join ContactHeadImgUrl on Contact.UserName = ContactHeadImgUrl.usrName
              where  Type=3 and Alias is not null 
              order by PYInitial
              '''
        cursor.execute(sql)
        result = cursor.fetchall()
    finally:
        lock.release()
    # DB.commit()
    return result


def close():
    global DB
    if DB:
        DB.close()


if __name__ == '__main__':
    get_contact()
