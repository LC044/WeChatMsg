import os.path
import random
import sqlite3
import threading
import traceback
from collections import defaultdict
from datetime import datetime, date
from typing import Tuple, List, Optional, Dict, Any

from app.DataBase.db_pool import db_pool
from app.log import logger
from app.util.compress_content import parser_reply
from app.util.protocbuf.msg_pb2 import MessageBytesExtra

db_path = "./app/Database/Msg/MSG.db"
lock = threading.Lock()


def is_database_exist():
    return os.path.exists(db_path)


def convert_to_timestamp_(time_input) -> int:
    if isinstance(time_input, (int, float)):
        # 如果输入是时间戳，直接返回
        return int(time_input)
    elif isinstance(time_input, str):
        # 如果输入是格式化的时间字符串，将其转换为时间戳
        try:
            dt_object = datetime.strptime(time_input, '%Y-%m-%d %H:%M:%S')
            return int(dt_object.timestamp())
        except ValueError:
            # 如果转换失败，可能是其他格式的字符串，可以根据需要添加更多的处理逻辑
            print("Error: Unsupported date format")
            return -1
    elif isinstance(time_input, date):
        # 如果输入是datetime.date对象，将其转换为时间戳
        dt_object = datetime.combine(time_input, datetime.min.time())
        return int(dt_object.timestamp())
    else:
        print("Error: Unsupported input type")
        return -1


def convert_to_timestamp(time_range) -> Tuple[int, int]:
    """
    将时间转换成时间戳
    @param time_range:
    @return:
    """
    if not time_range:
        return 0, 0
    else:
        return convert_to_timestamp_(time_range[0]), convert_to_timestamp_(time_range[1])


def parser_chatroom_message(messages):
    from app.DataBase import micro_msg_db, misc_db
    from app.util.protocbuf.msg_pb2 import MessageBytesExtra
    from app.person import Contact, Me, ContactDefault
    '''
    获取一个群聊的聊天记录
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
        a[12]: DisplayContent,
        a[13]: msg_sender, （ContactPC 或 ContactDefault 类型，这个才是群聊里的信息发送人，不是群聊或者自己是发送者没有这个字段）
    '''
    updated_messages = []  # 用于存储修改后的消息列表
    for row in messages:
        message = list(row)
        if message[4] == 1:  # 自己发送的就没必要解析了
            message.append(Me())
            updated_messages.append(tuple(message))
            continue
        if message[10] is None:  # BytesExtra是空的跳过
            message.append(ContactDefault(wxid))
            updated_messages.append(tuple(message))
            continue
        msgbytes = MessageBytesExtra()
        msgbytes.ParseFromString(message[10])
        wxid = ''
        for tmp in msgbytes.message2:
            if tmp.field1 != 1:
                continue
            wxid = tmp.field2
        if wxid == "":  # 系统消息里面 wxid 不存在
            message.append(ContactDefault(wxid))
            updated_messages.append(tuple(message))
            continue
        # todo 解析还是有问题，会出现这种带:的东西
        if ':' in wxid:  # wxid_ewi8gfgpp0eu22:25319:1
            wxid = wxid.split(':')[0]
        contact_info_list = micro_msg_db.get_contact_by_username(wxid)
        if contact_info_list is None:  # 群聊中已退群的联系人不会保存在数据库里
            message.append(ContactDefault(wxid))
            updated_messages.append(tuple(message))
            continue
        contact_info = {
            'UserName': contact_info_list[0],
            'Alias': contact_info_list[1],
            'Type': contact_info_list[2],
            'Remark': contact_info_list[3],
            'NickName': contact_info_list[4],
            'smallHeadImgUrl': contact_info_list[7]
        }
        contact = Contact(contact_info)
        contact.smallHeadImgBLOG = misc_db.get_avatar_buffer(contact.wxid)
        contact.set_avatar(contact.smallHeadImgBLOG)
        message.append(contact)
        updated_messages.append(tuple(message))
    return updated_messages


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
        self.open_flag = False
        self.init_database()

    def init_database(self, path=None):
        global db_path
        if not self.open_flag:
            if path:
                db_path = path
            if os.path.exists(db_path):
                self.open_flag = True
                if lock.locked():
                    lock.release()

    def add_sender(self, messages):
        """
        @param messages:
        @return:
        """
        new_messages = []
        for message in messages:
            is_sender = message[4]
            wxid = ''
            if is_sender:
                pass
            else:
                msgbytes = MessageBytesExtra()
                msgbytes.ParseFromString(message[10])
                for tmp in msgbytes.message2:
                    if tmp.field1 != 1:
                        continue
                    wxid = tmp.field2
            new_message = (*message, wxid)
            new_messages.append(new_message)
        return new_messages

    def get_messages(
            self,
            username_,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ):
        """
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
            a[12]: DisplayContent,
        """
        if not self.open_flag:
            return []
        
        begin_time, end_time = convert_to_timestamp(time_range)
        
        sql = '''
            SELECT 
                localId, 
                TalkerId, 
                Type, 
                SubType, 
                IsSender, 
                CreateTime, 
                Status, 
                StrContent, 
                strftime('%Y-%m-%d %H:%M:%S', datetime(CreateTime, 'unixepoch', 'localtime')), 
                MsgSvrID, 
                BytesExtra, 
                CompressContent, 
                DisplayContent 
            FROM MSG 
            WHERE StrTalker = ? 
            AND (? = 0 OR CreateTime >= ?) 
            AND (? = 0 OR CreateTime <= ?) 
            ORDER BY CreateTime DESC
        '''
        
        params = (username_, begin_time, begin_time, end_time, end_time)
        
        try:
            results = db_pool.execute_query(db_path, sql, params)
            
            # 处理群聊信息
            if results and username_.startswith('chatroom'):
                results = parser_chatroom_message(results)
            
            return results
        except Exception as e:
            logger.error(f"获取聊天记录失败: {e}\n{traceback.format_exc()}")
            return []

    def batch_insert_messages(self, messages_data: List[Dict[str, Any]]) -> bool:
        """
        批量插入消息数据
        
        Args:
            messages_data: 消息数据列表，每个字典包含一条消息的所有字段
            
        Returns:
            bool: 是否成功插入
        """
        if not self.open_flag or not messages_data:
            return False
            
        # 构建插入SQL
        sql = '''
            INSERT INTO MSG (
                MsgId, TalkerId, Type, SubType, IsSender, CreateTime, 
                Status, StrContent, StrTalker, MsgSvrID, BytesExtra, 
                CompressContent, DisplayContent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        # 准备参数列表
        params_list = [
            (
                msg.get('MsgId', ''), 
                msg.get('TalkerId', ''), 
                msg.get('Type', 0), 
                msg.get('SubType', 0),
                msg.get('IsSender', 0), 
                msg.get('CreateTime', int(time.time())),
                msg.get('Status', 0), 
                msg.get('StrContent', ''), 
                msg.get('StrTalker', ''),
                msg.get('MsgSvrID', ''), 
                msg.get('BytesExtra', None), 
                msg.get('CompressContent', None),
                msg.get('DisplayContent', None)
            )
            for msg in messages_data
        ]
        
        try:
            db_pool.execute_batch(db_path, sql, params_list)
            return True
        except Exception as e:
            logger.error(f"批量插入消息失败: {e}\n{traceback.format_exc()}")
            return False

    def get_messages_all(self, time_range=None):
        """
        获取所有聊天记录
        @param time_range:
        @return:
        """
        if not self.open_flag:
            return []
            
        begin_time, end_time = convert_to_timestamp(time_range)
        
        sql = '''
            SELECT 
                localId, 
                TalkerId, 
                Type, 
                SubType, 
                IsSender, 
                CreateTime, 
                Status, 
                StrContent, 
                strftime('%Y-%m-%d %H:%M:%S', datetime(CreateTime, 'unixepoch', 'localtime')), 
                MsgSvrID, 
                BytesExtra, 
                CompressContent, 
                DisplayContent,
                StrTalker
            FROM MSG
            WHERE (? = 0 OR CreateTime >= ?)
            AND (? = 0 OR CreateTime <= ?)
            ORDER BY CreateTime DESC
        '''
        
        params = (begin_time, begin_time, end_time, end_time)
        
        try:
            return db_pool.execute_query(db_path, sql, params)
        except Exception as e:
            logger.error(f"获取所有聊天记录失败: {e}\n{traceback.format_exc()}")
            return []

    def get_messages_group_by_day(
            self,
            username_: str,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,

    ) -> dict:
        """
        return dict {
            date: messages
        }
        """
        if not self.open_flag:
            return {}
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent,DisplayContent
            from MSG
            where StrTalker=? AND type=1
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            order by CreateTime;
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        result = parser_chatroom_message(result) if username_.__contains__('@chatroom') else result

        # 按天分组存储聊天记录
        grouped_results = defaultdict(list)
        for row in result:
            '2024-01-01'
            date = row[8][:10]  # 获取日期部分
            grouped_results[date].append(row)  # 将消息加入对应的日期列表中

        return grouped_results

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
                select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent,DisplayContent
                from MSG
                where StrTalker = ? and localId < ? and (Type=1 or Type=3)
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
        return parser_chatroom_message(result) if username_.__contains__('@chatroom') else result

    def get_messages_by_type(
            self,
            username_,
            type_,
            year_='all',
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ):
        """
        @param username_:
        @param type_:
        @param year_:
        @param time_range: Tuple(timestamp:开始时间戳,timestamp:结束时间戳)
        @return:
        """
        if not self.open_flag:
            return None
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        if year_ == 'all':
            sql = f'''
                        select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent,DisplayContent
                        from MSG
                        where StrTalker=? and Type=? 
                        {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
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
                select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra,CompressContent,DisplayContent
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

    def get_messages_by_keyword(self, username_, keyword, num=5, max_len=10, time_range=None, year_='all'):
        if not self.open_flag:
            return None
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
            select localId,TalkerId,Type,SubType,IsSender,CreateTime,Status,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,MsgSvrID,BytesExtra
            from MSG
            where StrTalker=? and Type=1 and LENGTH(StrContent)<? and StrContent like ?
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
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

    def get_messages_calendar(self, username_):
        sql = '''
            SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                WHERE StrTalker = ?
                ORDER BY CreateTime
            )
            group by days
        '''
        if not self.open_flag:
            print('数据库未就绪')
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        return [date[0] for date in result]

    def get_messages_by_days(
            self,
            username_,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ):
        result = None
        if not self.open_flag:
            return None
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
            SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                WHERE StrTalker = ?
                {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            )
            group by days
        '''
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        finally:
            lock.release()
        return result

    def get_messages_by_month(
            self,
            username_,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ):
        result = None
        if not self.open_flag:
            return None
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
            SELECT strftime('%Y-%m',CreateTime,'unixepoch','localtime') as days,count(MsgSvrID)
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                WHERE StrTalker = ?
                {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            )
            group by days
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_messages_by_hour(self, username_, time_range=None, year_='all'):
        result = []
        if not self.open_flag:
            return result
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
            SELECT strftime('%H:00',CreateTime,'unixepoch','localtime') as hours,count(MsgSvrID)
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                where StrTalker = ?
                {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
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
        return result

    def get_first_time_of_message(self, username_=''):
        if not self.open_flag:
            return None
        sql = f'''
            select StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime
            from MSG
            {'where StrTalker=?' if username_ else ''}
            order by CreateTime
            limit 1
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_] if username_ else [])
            result = self.cursor.fetchone()
        finally:
            lock.release()
        return result

    def get_latest_time_of_message(self, username_='', time_range=None, year_='all'):
        if not self.open_flag:
            return None
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f'''
                SELECT isSender,StrContent,strftime('%Y-%m-%d %H:%M:%S',CreateTime,'unixepoch','localtime') as StrTime,
                strftime('%H:%M:%S', CreateTime,'unixepoch','localtime') as hour
                FROM MSG
                WHERE Type=1 AND 
                {'StrTalker = ? AND ' if username_ else f"'{username_}'=? AND "} 
                hour BETWEEN '00:00:00' AND '05:00:00'
                {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
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

    def get_send_messages_type_number(
            self,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> list:
        """
        统计自己发的各类型消息条数，按条数降序，精确到subtype\n
        return [(type_1, subtype_1, number_1), (type_2, subtype_2, number_2), ...]\n
        be like [(1, 0, 71481), (3, 0, 6686), (49, 57, 3887), ..., (10002, 0, 1)]
        """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f"""
            SELECT type, subtype, Count(MsgSvrID)
            from MSG
            where isSender = 1
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            group by type, subtype
            order by Count(MsgSvrID) desc
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_messages_number(
            self,
            username_,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> int:
        """
        统计好友聊天消息的数量
        @param username_:
        @param time_range:
        @return:
        """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f"""
            SELECT Count(MsgSvrID)
            from MSG
            where StrTalker = ?
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
        """
        result = 0
        if not self.open_flag:
            return 0
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [username_])
            result = self.cursor.fetchone()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result[0] if result else 0

    def get_chatted_top_contacts(
            self,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
            contain_chatroom=False,
            top_n=10
    ) -> list:
        """
        统计聊天最多的 n 个联系人（默认不包含群组），按条数降序\n
        return [(wxid_1, number_1), (wxid_2, number_2), ...]
        """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f"""
            SELECT strtalker, Count(MsgSvrID)
            from MSG
            where strtalker != "filehelper" and strtalker != "notifymessage" and strtalker not like "gh_%"
            {"and strtalker not like '%@chatroom'" if not contain_chatroom else ""}
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            group by strtalker
            order by Count(MsgSvrID) desc
            limit {top_n}
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_send_messages_length(
            self,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> int:
        """
        统计自己总共发消息的字数，包含type=1的文本和type=49,subtype=57里面自己发的文本
        """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql_type_1 = f"""
            SELECT sum(length(strContent))
            from MSG
            where isSender = 1 and type = 1
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
        """
        sql_type_49 = f"""
            SELECT CompressContent
            from MSG
            where isSender = 1 and type = 49 and subtype = 57
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
        """
        sum_type_1 = None
        result_type_49 = None
        sum_type_49 = 0

        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql_type_1)
            sum_type_1 = self.cursor.fetchall()[0][0]
            self.cursor.execute(sql_type_49)
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

    def get_send_messages_number_sum(
            self,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> int:
        """统计自己总共发了多少条消息"""
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f"""
            SELECT count(MsgSvrID)
            from MSG
            where isSender = 1
            {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()[0][0]
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_send_messages_number_by_hour(
            self,
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> list:
        """
        统计每个（小时）时段自己总共发了多少消息，从最多到最少排序\n
        return be like [('23', 9526), ('00', 7890), ('22', 7600),  ..., ('05', 29)]
        """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql = f"""
            SELECT strftime('%H', CreateTime, 'unixepoch', 'localtime') as hour,count(MsgSvrID)
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                where isSender = 1
                    {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
            )
            group by hour
            order by count(MsgSvrID) desc
        """
        result = None
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        return result

    def get_message_length(
            self,
            username_='',
            time_range: Tuple[int | float | str | date, int | float | str | date] = None,
    ) -> int:
        """
                统计自己总共发消息的字数，包含type=1的文本和type=49,subtype=57里面自己发的文本
                """
        if time_range:
            start_time, end_time = convert_to_timestamp(time_range)
        sql_type_1 = f"""
                    SELECT sum(length(strContent))
                    from MSG
                    where  StrTalker = ? and
                    type = 1
                    {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
                """
        sql_type_49 = f"""
                    SELECT CompressContent
                    from MSG
                    where  StrTalker = ? and
                    type = 49 and subtype = 57
                    {'AND CreateTime>' + str(start_time) + ' AND CreateTime<' + str(end_time) if time_range else ''}
                """
        sum_type_1 = 0
        result_type_1 = 0
        result_type_49 = 0
        sum_type_49 = 0

        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            self.cursor.execute(sql_type_1, [username_])
            result_type_1 = self.cursor.fetchall()[0][0]
            self.cursor.execute(sql_type_49, [username_])
            result_type_49 = self.cursor.fetchall()
        except sqlite3.DatabaseError:
            logger.error(f'{traceback.format_exc()}\n数据库损坏请删除msg文件夹重试')
        finally:
            lock.release()
        for message in result_type_49:
            message = message[0]
            content = parser_reply(message)
            if content["is_error"]:
                continue
            sum_type_49 += len(content["title"])
        sum_type_1 = result_type_1 if result_type_1 else 0
        return sum_type_1 + sum_type_49

    def close(self):
        """关闭数据库连接，不再需要显式关闭，由连接池管理"""
        self.open_flag = False

    def __del__(self):
        self.close()


if __name__ == '__main__':
    db_path = "./Msg/MSG.db"
    msg = Msg()
    msg.init_database()
    wxid = 'wxid_0o18ef858vnu22'
    wxid = '24521163022@chatroom'
    wxid = 'wxid_vtz9jk9ulzjt22'  # si
    print()
    time_range = ('2023-01-01 00:00:00', '2024-01-01 00:00:00')
    print(msg.get_messages_calendar(wxid))
    print(msg.get_first_time_of_message())
    print(msg.get_latest_time_of_message())
    top_n = msg.get_chatted_top_contacts(time_range=time_range, top_n=9999999)
    print(top_n)
    print(len(top_n))
