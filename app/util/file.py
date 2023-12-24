import os
import traceback
import shutil

import requests

from app.log import log, logger
from app.util.protocbuf.msg_pb2 import MessageBytesExtra
from ..person import MePC

root_path = './data/files/'
if not os.path.exists('./data'):
    os.mkdir('./data')
if not os.path.exists(root_path):
    os.mkdir(root_path)


class File:
    def __init__(self):
        self.open_flag = False


def get_file(bytes_extra, thumb=False, output_path=root_path) -> str:
    try:
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytes_extra)
        file_original_path = ''
        file_path = ''
        file_name = ''
        real_path = ''
        if len(msg_bytes.message2) > 0:
            file_field = msg_bytes.message2[-1].field2
            if file_field.find('sec_msg_node') == -1:
                file_original_path = file_field
                file_name = os.path.basename(file_original_path)
                if file_name != '' and file_name != MePC().wxid:
                    file_path = os.path.join(output_path, file_name)
                    if os.path.exists(file_path):
                        print('文件' + file_path + '已存在')
                        return file_path
                    if os.path.isabs(file_original_path):
                        if os.path.exists(file_original_path):
                            real_path = file_original_path
                        else:  # 如果没找到再判断一次是否是迁移了目录
                            if file_original_path.find(r"FileStorage") != -1:
                                real_path = MePC().wx_dir + file_original_path[
                                                            file_original_path.find("FileStorage") - 1:]
                    else:
                        if file_original_path.find(MePC().wxid) != -1:
                            real_path = MePC().wx_dir + file_original_path.replace(MePC().wxid, '')
                        else:
                            real_path = MePC().wx_dir + file_original_path
                    if real_path != "":
                        if os.path.exists(real_path):
                            print('开始获取文件' + real_path)
                            shutil.copy2(real_path, file_path)
                        else:
                            print('文件' + file_original_path + '已丢失')
                            file_path = ''
        return file_path
    except:
        logger.error(traceback.format_exc())
        return ""
