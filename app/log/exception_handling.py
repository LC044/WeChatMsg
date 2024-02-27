import sqlite3
import sys
import traceback

import requests

from app.person import Me


class ExceptionHanding:
    def __init__(self, exc_type, exc_value, traceback_):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.traceback = traceback_
        self.error_message = ''.join(traceback.format_exception(exc_type, exc_value, traceback_))

    def parser_exc(self):
        if isinstance(self.exc_value, PermissionError):
            return f'权限错误，请使用管理员身份运行并将文件夹设置为可读写'
        elif isinstance(self.exc_value, sqlite3.DatabaseError):
            return '数据库错误，请删除app文件夹后重启电脑再运行软件'
        elif isinstance(self.exc_value, OSError) and self.exc_value.errno == 28:
            return '空间磁盘不足，请预留足够多的磁盘空间以供软件正常运行'
        elif isinstance(self.exc_value, TypeError) and 'NoneType' in str(self.exc_value) and 'not iterable' in str(
                self.exc_value):
            return '数据库错误，请删除app文件夹后重启电脑再运行软件'
        elif isinstance(self.exc_value,KeyboardInterrupt):
            return ''
        else:
            return '未知错误类型，可参考 https://blog.lc044.love/post/7 解决该问题\n温馨提示：重启电脑可解决80%的问题'

    def __str__(self):
        errmsg = f'{self.error_message}\n{self.parser_exc()}'
        return errmsg


def excepthook(exc_type, exc_value, traceback_):
    # 将异常信息转为字符串

    # 在这里处理全局异常

    error_message = ExceptionHanding(exc_type, exc_value, traceback_)
    txt = '您可添加QQ群发送log文件以便解决该问题'
    msg = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\ndetails: {error_message}\n\n{txt}"
    print(msg)

    # 调用原始的 excepthook，以便程序正常退出
    sys.__excepthook__(exc_type, exc_value, traceback_)

def send_error_msg( message):
    url = "http://api.lc044.love/error"
    if not message:
        return {
            'code': 201,
            'errmsg': '日志为空'
        }
    data = {
        'username': Me().wxid,
        'error': message
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            resp_info = response.json()
            return resp_info
        else:
            return {
                'code': 503,
                'errmsg': '服务器错误'
            }
    except:
        return {
            'code': 404,
            'errmsg': '客户端错误'
        }
