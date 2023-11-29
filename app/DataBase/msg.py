import os.path
import sqlite3
import threading
from pprint import pprint

DB = None
cursor = None
db_path = "./app/Database/Msg/MSG.db"
lock = threading.Lock()

# misc_path = './Msg/Misc.db'
if os.path.exists(db_path):
    DB = sqlite3.connect(db_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def is_database_exist():
    return os.path.exists(db_path)


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(db_path):
            DB = sqlite3.connect(db_path, check_same_thread=False)
            # '''创建游标'''
            cursor = DB.cursor()


def get_messages(username_):
    sql = '''
        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
        from MSG
        where StrTalker=?
        order by CreateTime
    '''
    try:
        lock.acquire(True)
        cursor.execute(sql, [username_])
        result = cursor.fetchall()
    finally:
        lock.release()
    result.sort(key=lambda x: x[5])
    return result


def get_messages_all():
    sql = '''
        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
        from MSG
        order by CreateTime
    '''
    try:
        lock.acquire(True)
        cursor.execute(sql)
        result = cursor.fetchall()
    finally:
        lock.release()
    result.sort(key=lambda x: x[5])
    return result


def get_message_by_num(username_, local_id):
    sql = '''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
            from MSG
            where StrTalker = ? and localId < ?
            order by CreateTime desc 
            limit 10 
        '''
    try:
        lock.acquire(True)
        cursor.execute(sql, [username_, local_id])
        result = cursor.fetchall()
    finally:
        lock.release()
    # result.sort(key=lambda x: x[5])
    return result


def close():
    for db in DB:
        db.close()


if __name__ == '__main__':
    msg_root_path = './Msg/'
    init_database()

    # username = 'wxid_0o18ef858vnu22'
    # result = get_messages(username)
    # pprint(result)
    # pprint(len(result))
    result = get_message_by_num('wxid_0o18ef858vnu22', 9999999)
    print(result)
    print(result[-1][0])
    local_id = result[-1][0]
    pprint(get_message_by_num('wxid_0o18ef858vnu22', local_id))
