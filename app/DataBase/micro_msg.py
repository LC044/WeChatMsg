import os.path
import sqlite3
import threading

lock = threading.Lock()
DB = None
cursor = None
db_path = "./app/Database/Msg/MicroMsg.db"


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


def is_database_exist():
    return os.path.exists(db_path)

lockMSG = threading.Lock()
DBMSG = None
cursorMSG = None
db_msg_path = "./app/Database/Msg/MSG.db"

@singleton
class MicroMSGMsg:
    def __init__(self):
        self.DBMSG = None
        self.cursorMSG = None
        self.open_flag = False
        self.init_database()

    def init_database(self):
        if not self.open_flag:
            if os.path.exists(db_msg_path):
                self.DBMSG = sqlite3.connect(db_msg_path, check_same_thread=False)
                # '''创建游标'''
                self.cursorMSG = self.DBMSG.cursor()
                self.open_flag = True
                if lockMSG.locked():
                    lockMSG.release()

    def get_contact(self, contacts):
        if not self.open_flag:
            return None
        try:
            lockMSG.acquire(True)
            sql = '''select StrTalker, MAX(CreateTime) from MSG group by StrTalker'''
            self.cursorMSG.execute(sql)
            res = self.cursorMSG.fetchall()
            res = {StrTalker: CreateTime for StrTalker, CreateTime in res}
            contacts = [list(cur_contact) for cur_contact in contacts]
            for i, cur_contact in enumerate(contacts):
                if cur_contact[0] in res:
                    contacts[i].append(res[cur_contact[0]])
                else:
                    contacts[i].append(0)
            contacts.sort(key=lambda cur_contact: cur_contact[-1], reverse=True)
        finally:
            lockMSG.release()
        return contacts

    def close(self):
        if self.open_flag:
            try:
                lockMSG.acquire(True)
                self.open_flag = False
                self.DBMSG.close()
            finally:
                lockMSG.release()

    def __del__(self):
        self.close()


@singleton
class MicroMsg:
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

    def get_contact(self):
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            sql = '''SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl
                    FROM Contact
                    INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                    WHERE Type % 2 = 1
                        AND NickName != ''
                    ORDER BY 
                        CASE
                            WHEN RemarkPYInitial = '' THEN PYInitial
                            ELSE RemarkPYInitial
                        END ASC
                  '''
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        finally:
            lock.release()
        return MicroMSGMsg().get_contact(result)

    def get_contact_by_username(self, username):
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            sql = '''SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl
                               FROM Contact
                               INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                               WHERE UserName = ?
                             '''
            self.cursor.execute(sql, [username])
            result = self.cursor.fetchone()
        finally:
            lock.release()
        return result

    def get_chatroom_info(self, chatroomname):
        '''
        获取群聊信息
        '''
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            sql = '''SELECT ChatRoomName, RoomData FROM ChatRoom WHERE ChatRoomName = ?'''
            self.cursor.execute(sql, [chatroomname])
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
    pass
    # get_contact()
