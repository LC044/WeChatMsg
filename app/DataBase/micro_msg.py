import os.path
import sqlite3
import threading

lock = threading.Lock()
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
            return []
        try:
            lock.acquire(True)
            sql = '''SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,COALESCE(ContactLabel.LabelName, 'None') AS labelName
                    FROM Contact
                    INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                    LEFT JOIN ContactLabel ON Contact.LabelIDList = ContactLabel.LabelId
                    WHERE (Type!=4 AND VerifyFlag=0)
                        AND NickName != ''
                    ORDER BY 
                        CASE
                            WHEN RemarkPYInitial = '' THEN PYInitial
                            ELSE RemarkPYInitial
                        END ASC
                  '''
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except sqlite3.OperationalError:
            # lock.acquire(True)
            sql = '''
                   SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,"None"
                   FROM Contact
                   INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                   WHERE (Type!=4 AND VerifyFlag=0)
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
        from app.DataBase import msg_db
        return msg_db.get_contact(result)

    def get_contact_by_username(self, username):
        if not self.open_flag:
            return None
        try:
            lock.acquire(True)
            sql = '''
                   SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,ContactLabel.LabelName
                   FROM Contact
                   INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                   LEFT JOIN ContactLabel ON Contact.LabelIDList = ContactLabel.LabelId
                   WHERE UserName = ?
                '''
            self.cursor.execute(sql, [username])
            result = self.cursor.fetchone()
        except sqlite3.OperationalError:
            # 解决ContactLabel表不存在的问题
            # lock.acquire(True)
            sql = '''
                   SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,"None"
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
    db_path = "./app/database/Msg/MicroMsg.db"
    msg = MicroMsg()
    msg.init_database()
    contacts = msg.get_contact()
    from app.DataBase.hard_link import decodeExtraBuf

    s = {'wxid_vtz9jk9ulzjt22','wxid_zu9l4wxdv1pa22', 'wxid_0o18ef858vnu22','wxid_8piw6sb4hvfm22','wxid_e7ypfycxpnu322','wxid_oxmg02c8kwxu22','wxid_7pp2fblq7hkq22','wxid_h1n9niofgyci22'}
    for contact in contacts:
        if contact[0] in s:
            print(contact[:7])
            buf = contact[9]
            info = decodeExtraBuf(buf)
            print(info)
