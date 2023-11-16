import os.path
import re
import sqlite3

DB = []
cursor = []
msg_root_path = "./app/Database/Msg/"
# misc_path = './Msg/Misc.db'
if os.path.exists(msg_root_path):
    for root, dirs, files in os.walk(msg_root_path):
        for file in files:
            if re.match('^MSG[0-9]+\.db$', file):
                # print('ok', file)
                msg_path = os.path.join(msg_root_path, file)
                DB0 = sqlite3.connect(msg_path, check_same_thread=False)
                # '''创建游标'''
                cursor0 = DB0.cursor()
                DB.append(DB0)
                cursor.append(cursor0)


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(msg_root_path):
            for root, dirs, files in os.walk(msg_root_path):
                for file in files:
                    # print(file)
                    if re.match('^MSG[0-9]+\.db$', file):
                        print('ok', file)
                        msg_path = os.path.join(msg_root_path, file)
                        DB0 = sqlite3.connect(msg_path, check_same_thread=False)
                        # '''创建游标'''
                        cursor0 = DB0.cursor()
                        DB.append(DB0)
                        cursor.append(cursor0)


def get_messages(username_):
    sql = '''
        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
        from MSG
        where StrTalker=?
        order by CreateTime
    '''
    result = []
    for cur in cursor:
        cur.execute(sql, [username_])
        result_ = cur.fetchall()
        # print(len(result))
        result += result_
    result.sort(key=lambda x: x[5])
    return result


def close():
    for db in DB:
        db.close()


if __name__ == '__main__':
    from pprint import pprint

    msg_root_path = './Msg/'
    init_database()

    username = 'wxid_0o18ef858vnu22'
    result = get_messages(username)
    pprint(result)
    pprint(len(result))
