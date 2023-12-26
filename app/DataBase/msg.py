import os.path
import random
import sqlite3
import threading
import traceback


from app.log import logger
from app.util.compress_content import parser_reply

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
        '''
        return list
            a[0]: localId,
            a[1]: talkerId, （和strtalker对应的，不是群聊信息发送人）
            a[2]: type,
            a[3]: subType,
            a[4]: is_sender,
            a[5]: timestamp,
            a[6]: status, （没啥用）
            a[7]: str_content,
            a[8]: str_time, （格式化的时间）
            a[9]: msgSvrId,
            a[10]: BytesExtra,
            a[11]: CompressContent,
        '''
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

    def get_messages_by_type(self, username_, type_, year_='all'):
        if not self.open_flag:
            return None
        if year_ == 'all':
            sql = '''
                        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
                        from MSG
                        where StrTalker=? and Type=? 
                        order by CreateTime
                    '''
            try:
                lock.acquire(True)
                self.cursor.execute(sql, [username_, type_])
                result = self.cursor.fetchall()
            finally:
                lock.release()
        else:
            sql = '''
                            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent
                            from MSG
                            where StrTalker=? and Type=? and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?
                            order by CreateTime
                        '''
            try:
                lock.acquire(True)
                self.cursor.execute(sql, [username_, type_, year_])
            finally:
                lock.release()
                result = self.cursor.fetchall()
        return result

    def get_messages_by_keyword(self, username_, keyword, num=5, max_len=10, year_='all'):
        if not self.open_flag:
            return None
        sql = f'''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra
            from MSG
            where StrTalker=? and Type=1 and LENGTH(StrContent)<? and StrContent like ?
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
            order by CreateTime desc
        '''
        temp = []
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_, max_len, f'%{keyword}%'] if year_ == "all" else [username_, max_len,
                                                                                                  f'%{keyword}%',
                                                                                                  year_])
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
        """
        返回值为一个列表，每个列表元素是一个对话
        每个对话是一个元组数据
        ('is_send','时间戳','以关键词为分割符的消息内容','格式化时间')
        """
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

    def get_messages_by_hour(self, username_, year_='all'):
        result = []
        if not self.open_flag:
            return result
        if year_ == 'all':
            sql = '''
                SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    where StrTalker = ?
                )
                group by hours
            '''
            try:
                lock.acquire(True)
                self.cursor.execute(sql, [username_])
            except sqlite3.DatabaseError:
                logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
            finally:
                lock.release()
                result = self.cursor.fetchall()
        else:
            sql = '''
                SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
                from (
                    SELECT MsgSvrID, CreateTime
                    FROM MSG
                    where StrTalker = ? and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?
                )
                group by hours
                '''
            try:
                lock.acquire(True)
                self.cursor.execute(sql, [username_, year_])
            except sqlite3.DatabaseError:
                logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
            finally:
                lock.release()
                result = self.cursor.fetchall()
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

    def get_latest_time_of_message(self, username_, year_='all'):
        if not self.open_flag:
            return None
        sql = f'''
                SELECT isSender,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,
                strftime('%H:%M:%S', CreateTime,'unixepoch','localtime') as hour
                FROM MSG
                WHERE StrTalker = ? AND Type=1 AND
                hour BETWEEN '00:00:00' AND '05:00:00'
                {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
                ORDER BY hour DESC
                LIMIT 20;
            '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_, year_] if year_ != "all" else [username_])
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
            result = self.cursor.fetchall()
        if not result:
            return []
        res = []
        is_sender = result[0][0]
        res.append(result[0])
        for msg in result[1:]:
            if msg[0] != is_sender:
                res.append(msg)
                break
        return res

    def get_send_messages_type_number(self, year_="all") -> list:
        """
        统计自己发的各类型消息条数，按条数降序，精确到subtype\n
        return [(type_1, subtype_1, number_1), (type_2, subtype_2, number_2), ...]\n
        be like [(1, 0, 71481), (3, 0, 6686), (49, 57, 3887), ..., (10002, 0, 1)]
        """

        sql = f"""
            SELECT type, subtype, Count(MsgSvrID)
            from MSG
            where isSender = 1
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
            group by type, subtype
            order by Count(MsgSvrID) desc
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [year_] if year_ != "all" else [])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_messages_number(self, username_, year_="all") -> int:
        sql = f"""
            SELECT Count(MsgSvrID)
            from MSG
            where StrTalker = ?
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
            group by type, subtype
            order by Count(MsgSvrID) desc
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_,year_] if year_ != "all" else [username_])
            result = self.cursor.fetchone()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result[0] if result else 0

    def get_chatted_top_contacts(self, year_="all", contain_chatroom=False, top_n=10) -> list:
        """
        统计聊天最多的 n 个联系人（默认不包含群组），按条数降序\n
        return [(wxid_1, number_1), (wxid_2, number_2), ...]
        """

        sql = f"""
            SELECT strtalker, Count(MsgSvrID)
            from MSG
            where strtalker != "filehelper" and strtalker != "notifymessage" and strtalker not like "gh_%"
            {"and strtalker not like '%@chatroom'" if not contain_chatroom else ""}
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
            group by strtalker
            order by Count(MsgSvrID) desc
            limit {top_n}
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [year_] if year_ != "all" else [])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_send_messages_length(self, year_="all") -> int:
        """
        统计自己总共发消息的字数，包含type=1的文本和type=49,subtype=57里面自己发的文本
        """

        sql_type_1 = f"""
            SELECT sum(length(strContent))
            from MSG
            where isSender = 1 and type = 1
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
        """
        sql_type_49 = f"""
            SELECT CompressContent
            from MSG
            where isSender = 1 and type = 49 and subtype = 57
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
        """
        sum_type_1 = None
        result_type_49 = None
        sum_type_49 = 0

        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql_type_1, [year_] if year_ != "all" else [])
            sum_type_1 = self.cursor.fetchall()[0][0]
            self.cursor.execute(sql_type_49, [year_] if year_ != "all" else [])
            result_type_49 = self.cursor.fetchall()
            for message in result_type_49:
                message = message[0]
                content = parser_reply(message)
                if content["is_error"]:
                    continue
                sum_type_49 += len(content["title"])
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return sum_type_1 + sum_type_49

    def get_send_messages_number_sum(self, year_="all") -> int:
        """统计自己总共发了多少条消息"""

        sql = f"""
            SELECT count(MsgSvrID)
            from MSG
            where isSender = 1
            {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [year_] if year_ != "all" else [])
            result = self.cursor.fetchall()[0][0]
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_send_messages_number_by_hour(self, year_="all"):
        """
        统计每个（小时）时段自己总共发了多少消息，从最多到最少排序\n
        return be like [('23', 9526), ('00', 7890), ('22', 7600),  ..., ('05', 29)]
        """
        sql = f"""
            SELECT strftime('%H', CreateTime, 'unixepoch', 'localtime') as hour,count(MsgSvrID)
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                where isSender = 1
                    {"and strftime('%Y', CreateTime, 'unixepoch', 'localtime') = ?" if year_ != "all" else ""}
            )
            group by hour
            order by count(MsgSvrID) desc
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [year_] if year_ != "all" else [])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
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
    db_path = "./app/database/Msg/MSG.db"
    msg = Msg()
    msg.init_database()
    print(msg.get_latest_time_of_message('wxid_0o18ef858vnu22', year_='2023'))
    print(msg.get_messages_number('wxid_0o18ef858vnu22', year_='2023'))
    print(msg.get_messages_by_type('wxid_0o18ef858vnu22',34))
