import os.path
import sqlite3
import threading

lock = threading.Lock()
DB = None
cursor = None
misc_path = "./app/Database/Msg/Misc.db"
# misc_path = './Msg/Misc.db'
if os.path.exists(misc_path):
    DB = sqlite3.connect(misc_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(misc_path):
            DB = sqlite3.connect(misc_path, check_same_thread=False)
            # '''创建游标'''
            cursor = DB.cursor()


def get_avatar_buffer(userName):
    sql = '''
        select smallHeadBuf
        from ContactHeadImg1
        where usrName=?;
    '''
    try:
        lock.acquire(True)
        try:
            cursor.execute(sql, [userName])
        except AttributeError:
            init_database()
        finally:
            cursor.execute(sql, [userName])
        result = cursor.fetchall()
        # print(result[0][0])
        if result:
            return result[0][0]
    finally:
        lock.release()
    return None


if __name__ == '__main__':
    get_avatar_buffer('wxid_al2oan01b6fn11')
