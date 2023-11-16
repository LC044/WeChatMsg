import os.path
import sqlite3

DB = None
cursor = None
msg_path = "./app/Database/Msg/MSG0.db"
# misc_path = './Msg/Misc.db'
if os.path.exists(msg_path):
    DB = sqlite3.connect(msg_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(msg_path):
            DB = sqlite3.connect(msg_path, check_same_thread=False)
            # '''创建游标'''
            cursor = DB.cursor()


def get_messages(username_):
    sql = '''
        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
        from MSG
        where StrTalker=?
        order by CreateTime
    '''
    cursor.execute(sql, [username_])
    result_ = cursor.fetchall()
    return result_


if __name__ == '__main__':
    from pprint import pprint

    msg_path = './Msg/MSG3.db'
    init_database()

    username = 'wxid_0o18ef858vnu22'
    result = get_messages(username)
    pprint(result)
    pprint(len(result))
