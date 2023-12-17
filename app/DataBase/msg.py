import os.path
import random
import html
import sqlite3
import threading
import traceback
from pprint import pprint
import lz4.block
import html
import re

from app.log import logger

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


class MsgType:
    TEXT = 1
    IMAGE = 3
    EMOJI = 47


class Msg:
    def __init__(self):
        self.DB = None
        self.cursor = None
        self.open_flag = False
        self.init_database()

    def init_database(self, path=None):
        global db_path
        if not self.open_flag:
            if path:
                db_path = path
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
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
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
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,StrTalker,Reserved1,CompressContent
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

    def get_messages_length(self):
        sql = '''
            select count(*)
            group by MsgSvrID
            from MSG
        '''
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except Exception as e:
            result = None
        finally:
            lock.release()
        return result[0]

    def get_message_by_num(self, username_, local_id):
        sql = '''
                select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
                from MSG
                where StrTalker = ? and localId < ?
                order by CreateTime desc 
                limit 20
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

    def get_messages_by_type(self, username_, type_, is_Annual_report_=False, year_='2023'):
        if not self.open_flag:
            return None
        if is_Annual_report_:
            sql = '''
                select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
                from MSG
                where StrTalker=? and Type=? and strftime('%Y',CreateTime,'unixepoch','localtime') = ?
                order by CreateTime
            '''
        else:
            sql = '''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
            from MSG
            where StrTalker=? and Type=?
            order by CreateTime
        '''
        try:
            lock.acquire(True)
            if is_Annual_report_:
                self.cursor.execute(sql, [username_, type_, year_])
            else:
                self.cursor.execute(sql, [username_, type_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        return result

    def get_messages_by_keyword(self, username_, keyword, num=5, max_len=10):
        if not self.open_flag:
            return None
        sql = '''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra
            from MSG
            where StrTalker=? and Type=1 and LENGTH(StrContent)<? and StrContent like ?
            order by CreateTime desc
        '''
        temp = []
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_, max_len, f'%{keyword}%'])
            messages = self.cursor.fetchall()
        finally:
            lock.release()
        if len(messages) > 5:
            messages = random.sample(messages, num)
        try:
            lock.acquire(True)
            for msg in messages:
                local_id = msg[0]
                is_send = msg[4]
                sql = '''
                    select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID
                    from MSG
                    where localId > ? and StrTalker=? and Type=1 and IsSender=?
                    limit 1
                '''
                self.cursor.execute(sql, [local_id, username_, 1 - is_send])
                temp.append((msg, self.cursor.fetchone()))
        finally:
            lock.release()
        res = []
        for dialog in temp:
            msg1 = dialog[0]
            msg2 = dialog[1]
            try:
                res.append((
                    (msg1[4], msg1[5], msg1[7].split(keyword), msg1[8]),
                    (msg2[4], msg2[5], msg2[7], msg2[8])
                ))
            except TypeError:
                res.append((
                    ('', '', ['', ''], ''),
                    ('', '', '', '')
                ))
        print(keyword,res)
        return res
    def get_contact(self, contacts):
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            sql = '''select StrTalker, MAX(CreateTime) from MSG group by StrTalker'''
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        finally:
            lock.release()
        res = {StrTalker: CreateTime for StrTalker, CreateTime in res}
        contacts = [list(cur_contact) for cur_contact in contacts]
        for i, cur_contact in enumerate(contacts):
            if cur_contact[0] in res:
                contacts[i].append(res[cur_contact[0]])
            else:
                contacts[i].append(0)
        contacts.sort(key=lambda cur_contact: cur_contact[-1], reverse=True)
        return contacts
    def get_messages_by_days(self, username_, is_Annual_report_=False, year_='2023'):
        if is_Annual_report_:
            sql = '''
                SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    WHERE StrTalker = ? AND strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?
                )
                group by days
            '''
        else:
            sql = '''
                SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    WHERE StrTalker = ?
                )
                group by days
            '''
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            if is_Annual_report_:
                self.cursor.execute(sql, [username_, year_])
            else:
                self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        return result

    def get_messages_by_month(self, username_, is_Annual_report_=False, year_='2023'):
        if is_Annual_report_:
            sql = '''
                SELECT strftime('%Y-%m',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    WHERE StrTalker = ? AND strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?
                )
                group by days
                '''
        else:
            sql = '''
                SELECT strftime('%Y-%m',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    WHERE StrTalker = ?
                )
                group by days
            '''
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            if is_Annual_report_:
                self.cursor.execute(sql, [username_, year_])
            else:
                self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        # result.sort(key=lambda x: x[5])
        return result

    def get_messages_by_hour(self, username_, is_Annual_report_=False, year_='2023'):
        if is_Annual_report_:
            sql = '''
                SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    where StrTalker = ? and strftime('%Y',CreateTime,'unixepoch','localtime') = ?
                )
                group by hours
                '''
        else:
            sql = '''
                SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    where StrTalker = ?
                )
                group by hours
            '''
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            if is_Annual_report_:
                self.cursor.execute(sql, [username_, year_])
            else:
                self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        # result.sort(key=lambda x: x[5])
        return result

    def get_first_time_of_message(self, username_):
        if not self.open_flag:
            return None
        sql = '''
            select StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
            from MSG
            where StrTalker=?
            order by CreateTime
            limit 1
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchone()
        finally:
            lock.release()
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
    result = msg.get_message_by_num('wxid_vtz9jk9ulzjt22', 9999999)
    print(result)
    result = msg.get_messages_by_type('wxid_vtz9jk9ulzjt22',49)
    for r in result:
        type_ = r[2]
        sub_type = r[3]
        if type_ == 49 and sub_type == 57:
            print(r)
            print(r[-1])
            break
