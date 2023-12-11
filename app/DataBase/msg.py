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

def decompress_CompressContent(data):
    """
    解压缩Msg：CompressContent内容
    :param data:
    :return:
    """
    if data is None or not isinstance(data, bytes):
        return None

    try:    
        dst = lz4.block.decompress(data, uncompressed_size=len(data) << 10)
        decoded_string = dst.decode().replace('\x00', '')  # Remove any null characters
    except lz4.block.LZ4BlockError:
        print("Decompression failed: potentially corrupt input or insufficient buffer size.") 
        return None

    # 处理 HTML 转义字符串如 &amp;gt; 等。可能会递归嵌套，我们只考虑原会话和第一级引用会话，不考虑更深的引用，故只执行两遍。
    uncompressed_data = html.unescape(decoded_string)
    uncompressed_data = html.unescape(uncompressed_data)

    return uncompressed_data

def transferMessages(messages, compress_content_column=-1, content_column=7):
  """
  将 MSG 中压缩的聊天内容（包含引用的聊天），解压后，以简单形式放入 content (只取前两级会话主题)
  :param compress_content_column: 压缩聊天所在列，-1 则为最后一列
  :param content_column: 聊天内容所在列
  :return:
  """
  new_messages = []
  for row in messages:
      mutable_row = list(row)
      type = row[2]
      sub_type = row[3]
      addition_idx = len(mutable_row) - 1 if compress_content_column == -1 else compress_content_column

      if type == 49 and sub_type == 57 and mutable_row[addition_idx] is not None:
          decoded_string = decompress_CompressContent(mutable_row[addition_idx])

          # 使用正则表达式查找所有的 <title> 标签内容
          title_regex = r'<title>(.*?)</title>'
          titles = re.findall(title_regex, decoded_string)

          if len(titles) >= 2:
              # 如果找到了至少两个 title，就把他们结合起来
              decoded_string = titles[0] + '<br/>引用：' + titles[1]
          # 否则，如果只找到一个 title，就只保留这一个
          elif len(titles) == 1:
              decoded_string = titles[0]

          mutable_row[content_column] = decoded_string
      row = tuple(mutable_row)
      new_messages.append(row)
  return new_messages


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
        return transferMessages(result)

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
        return transferMessages(result)

    def get_messages_length(self):
        sql = '''
            select count(*)
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
        return transferMessages(result)

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
        return transferMessages(result)

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
            res.append((
                (msg1[4], msg1[5], msg1[7].split(keyword), msg1[8]),
                (msg2[4], msg2[5], msg2[7], msg2[8])
            ))
        return res

    def get_messages_by_days(self, username_, is_Annual_report_=False, year_='2023'):
        if is_Annual_report_:
            sql = '''
                SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from MSG
                where StrTalker = ? and strftime('%Y',CreateTime,'unixepoch','localtime') = ?
                group by days
            '''
        else:
            sql = '''
                SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from MSG
                where StrTalker = ?
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
                    from MSG
                    where StrTalker = ? and strftime('%Y',CreateTime,'unixepoch','localtime') = ?
                    group by days
                '''
        else:
            sql = '''
                SELECT strftime('%Y-%m',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
                from MSG
                where StrTalker = ?
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
                    from MSG
                    where StrTalker = ? and strftime('%Y',CreateTime,'unixepoch','localtime') = ?
                    group by hours
                '''
        else:
            sql = '''
                SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
                from MSG
                where StrTalker = ?
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
    result = msg.get_message_by_num('wxid_0o18ef858vnu22', 9999999)
    print(result)
    result = msg.get_messages_by_type('wxid_0o18ef858vnu22',43)
    bytes_ = result[-1][-1]
    print(bytes_)
    print(bytes_)