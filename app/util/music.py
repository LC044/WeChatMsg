import os
import traceback
import shutil

from app.log import log, logger
from app.util.protocbuf.msg_pb2 import MessageBytesExtra
import requests
from urllib.parse import urlparse, parse_qs
import re

root_path = './data/music/'
if not os.path.exists('./data'):
    os.mkdir('./data')
if not os.path.exists(root_path):
    os.mkdir(root_path)


class File:
    def __init__(self):
        self.open_flag = False


def get_music_path(url, file_title, output_path=root_path) -> str:
    try:
        parsed_url = urlparse(url)
        if '.' in parsed_url.path:
            # 获取扩展名
            file_extension = parsed_url.path.split('.')[-1]

            pattern = r'[\\/:*?"<>|\r\n]+'
            file_title = re.sub(pattern, "_", file_title)
            file_name = file_title + '.' + file_extension
            music_path = os.path.join(output_path, file_name)
            if os.path.exists(music_path):
                # print('文件' + music_path + '已存在')
                return music_path
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.40 Safari/537.36 Edg/87.0.664.24'
            }
            requests.packages.urllib3.disable_warnings()
            response = requests.get(url,headers=header,verify=False)
            if response.status_code == 200:
                with open(music_path, 'wb') as f:
                    f.write(response.content)
            else:
                music_path = ''
                print("音乐" + file_name + "获取失败：请求地址：" + url)
        else:
            music_path = ''
            print('音乐文件已失效，url：' + url)
        return music_path
    except Exception as e:
        print(f"Get Music Path Error: {e}")
        logger.error(traceback.format_exc())
        return ""
