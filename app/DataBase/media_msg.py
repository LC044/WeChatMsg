import os.path
import sqlite3
import threading

lock = threading.Lock()
db_path = "./app/Database/Msg/MediaMSG3.db"


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class MediaMsg:
    def __init__(self):
        self.DB = None
        self.cursor: sqlite3.Cursor = None
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

    def get_media_buffer(self, reserved0):
        pass
        sql = '''
            select Buf
            from Media
            where Reserved0 = ?
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [reserved0])
            return self.cursor.fetchone()
        finally:
            lock.release()


if __name__ == '__main__':
    db_path = './Msg/MediaMSG3.db'
    media_msg_db = MediaMsg()
    reserved = '823076859361714342'
    buf = media_msg_db.get_media_buffer(reserved)
    print(buf)
