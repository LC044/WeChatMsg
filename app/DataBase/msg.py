import os.path
import sqlite3
import threading
import traceback
from pprint import pprint

from app.log import logger

DB = None
cursor = None
db_path = "./app/Database/Msg/MSG.db"
lock = threading.Lock()


def is_database_exist():
    return os.path.exists(db_path)


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class Msg:
    def __init__(self):
        self.DB = None
        self.cursor = None
        self.open_flag = False
        self.init_database()

    def init_database(self):
        if not self.open_flag:
            if os.path.exists(db_path):
                self.DB = sqlite3.connect(db_path, check_same_thread=False)
                # '''创建游标'''
                self.cursor = self.DB.cursor()
                self.open_flag = True
                if lock.locked():
                    lock.release()

    def get_messages(self, username_):
        if not self.open_flag:
            return None
        sql = '''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
            from MSG
            where StrTalker=?
            order by CreateTime
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        result.sort(key=lambda x: x[5])
        return result

    def get_messages_all(self):
        sql = '''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
            from MSG
            order by CreateTime
        '''
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        finally:
            lock.release()
        result.sort(key=lambda x: x[5])
        return result

    def get_message_by_num(self, username_, local_id):
        sql = '''
                select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
                from MSG
                where StrTalker = ? and localId < ?
                order by CreateTime desc 
                limit 10 
            '''
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_, local_id])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        # result.sort(key=lambda x: x[5])
        return result

    def close(self):
        if self.open_flag:
            try:
                lock.acquire(True)
                self.open_flag = False
                self.DB.close()
            finally:
                lock.release()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    db_path = "./Msg/MSG.db"
    msg = Msg()
    msg.init_database()
    result = msg.get_message_by_num('wxid_0o18ef858vnu22', 9999999)
    print(result)
    print(result[-1][0])
    local_id = result[-1][0]
    pprint(msg.get_message_by_num('wxid_0o18ef858vnu22', local_id))
