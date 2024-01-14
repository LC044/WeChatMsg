import os.path
import subprocess
import sys
import traceback
from os import system
import sqlite3
import threading
import xml.etree.ElementTree as ET
from pilk import decode

from app.log import logger

lock = threading.Lock()
db_path = "./app/Database/Msg/MediaMSG.db"


def get_ffmpeg_path():
    # 获取打包后的资源目录
    resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    # 构建 FFmpeg 可执行文件的路径
    ffmpeg_path = os.path.join(resource_dir, 'app', 'resources','data', 'ffmpeg.exe')

    return ffmpeg_path


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
            result = self.cursor.fetchone()

        finally:
            lock.release()
        return result[0] if result else None

    def get_audio(self, reserved0, output_path):
        buf = self.get_media_buffer(reserved0)
        if not buf:
            return ''
        silk_path = f"{output_path}/{reserved0}.silk"
        pcm_path = f"{output_path}/{reserved0}.pcm"
        mp3_path = f"{output_path}/{reserved0}.mp3"
        if os.path.exists(mp3_path):
            return mp3_path
        with open(silk_path, "wb") as f:
            f.write(buf)
        # open(silk_path, "wb").write()
        try:
            decode(silk_path, pcm_path, 44100)
            # 调用系统上的 ffmpeg 可执行文件
            # 获取 FFmpeg 可执行文件的路径
            ffmpeg_path = get_ffmpeg_path()
            # # 调用 FFmpeg
            if os.path.exists(ffmpeg_path):
                cmd = f'''"{ffmpeg_path}" -loglevel quiet -y -f s16le -i "{pcm_path}" -ar 44100 -ac 1 "{mp3_path}"'''
                # system(cmd)
                # 使用subprocess.run()执行命令
                subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # 源码运行的时候下面的有效
                # 这里不知道怎么捕捉异常
                cmd = f'''"{os.path.join(os.getcwd(), 'app', 'resources', 'data','ffmpeg.exe')}" -loglevel quiet -y -f s16le -i "{pcm_path}" -ar 44100 -ac 1 "{mp3_path}"'''
                # system(cmd)
                # 使用subprocess.run()执行命令
                subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.remove(silk_path)
            os.remove(pcm_path)
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f'语音发送错误\n{traceback.format_exc()}')
            cmd = f'''"{os.path.join(os.getcwd(), 'app', 'resources', 'data', 'ffmpeg.exe')}" -loglevel quiet -y -f s16le -i "{pcm_path}" -ar 44100 -ac 1 "{mp3_path}"'''
            # system(cmd)
            # 使用subprocess.run()执行命令
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        finally:
            print(mp3_path)
        return mp3_path

    def get_audio_path(self, reserved0, output_path):
        mp3_path = f"{output_path}\\{reserved0}.mp3"
        mp3_path = mp3_path.replace("/", "\\")
        return mp3_path

    def get_audio_text(self, content):
        try:
            root = ET.fromstring(content)
            transtext = root.find(".//voicetrans").get("transtext")
            return transtext
        except:
            return ""

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
    db_path = './Msg/MediaMSG.db'
    media_msg_db = MediaMsg()
    reserved = '2865682741418252473'
    path = media_msg_db.get_audio(reserved, r"D:\gou\message\WeChatMsg")
    print(path)
