import os.path
import sqlite3
import threading

lock = threading.Lock()
DB = None
cursor = None
db_path = "./app/Database/Msg/Misc.db"


# db_path = './Msg/Misc.db'


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class Misc:
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

    def get_avatar_buffer(self, userName):
        if not self.open_flag:
            return None
        sql = '''
            select smallHeadBuf
            from ContactHeadImg1
            where usrName=?;
        '''
        if not self.open_flag:
            self.init_database()
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [userName])
            result = self.cursor.fetchall()
            if result:
                return result[0][0]
        finally:
            lock.release()
        return None

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
    Misc()
    print(Misc().get_avatar_buffer('wxid_al2oan01b6fn11'))
