import os.path
from os import system
import sqlite3
import threading
import xml.etree.ElementTree as ET
from pilk import decode

lock = threading.Lock()
db_path = "./app/Database/Msg/MediaMSG.db"


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
        sql = '''
            select Buf
            from Media
            where Reserved0 = ?
        '''
        try:
            lock.acquire(True)
            self.cursor.execute(sql, [reserved0])
            return self.cursor.fetchone()[0]
        finally:
            lock.release()

    def get_audio(self, reserved0, output_path):
        buf = self.get_media_buffer(reserved0)
        silk_path = f"{output_path}\\{reserved0}.silk"
        pcm_path = f"{output_path}\\{reserved0}.pcm"
        mp3_path = f"{output_path}\\{reserved0}.mp3"
        slik_path = silk_path.replace("/", "\\")
        pcm_path = pcm_path.replace("/", "\\")
        mp3_path = mp3_path.replace("/", "\\")
        print(mp3_path)
        if os.path.exists(mp3_path):
            return mp3_path
        open(silk_path, "wb").write(buf)
        decode(silk_path, pcm_path, 44100)
        system(f'ffmpeg.exe -loglevel quiet -y -f s16le -i "{pcm_path}" -ar 44100 -ac 1 "{mp3_path}"')
        system(f'del "{silk_path}"')
        system(f'del "{pcm_path}"')
        return mp3_path

    def get_audio_text(self, content):
        try:
            root = ET.fromstring(content)
            transtext = root.find(".//voicetrans").get("transtext")
            return transtext
        except ET.ParseError:
            return ""


if __name__ == '__main__':
    db_path = './Msg/MediaMSG.db'
    media_msg_db = MediaMsg()
    reserved = '2865682741418252473'
    path = media_msg_db.get_audio(reserved, r"D:\gou\message\WeChatMsg")
    print(path)
