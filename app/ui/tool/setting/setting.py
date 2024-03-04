import json
import os.path
import time

import requests
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QMessageBox
from app.config import SEND_LOG_FLAG
from app.person import Me
from .settingUi import Ui_Form

Stylesheet = """
QPushButton{
    background-color: rgb(250,252,253);
    border-radius: 5px;
    padding: 8px;
    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
}
QPushButton:hover { 
    background-color: lightgray;
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 400px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
    color: black;
    border:none;
}
QListWidget::item{
    min-width: 80px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    border-left:none;
    color: black;
    font-weight: bold;
}
QCheckBox::indicator {
    background: rgb(251, 251, 251);
    Width:60px;
    Height:60px;
    border-radius: 10px;
}
QCheckBox::indicator:unchecked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_关闭.svg);
}
QCheckBox::indicator:checked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_开启.svg);
}

"""


def set_SEND_LOG_FLAG(flag):
    # noinspection PyGlobalUndefined
    global SEND_LOG_FLAG
    SEND_LOG_FLAG = flag


class SettingControl(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super(SettingControl, self).__init__(parent)
        self.setStyleSheet(Stylesheet)
        self.setupUi(self)

        self.btn_addstopword.clicked.connect(self.add_stopwords)
        self.btn_addnewword_2.clicked.connect(self.add_new_words)
        self.commandLinkButton_send_error_log.clicked.connect(self.show_info)
        self.btn_send_error_log.clicked.connect(self.send_error_log)
        self.init_ui()
        self.read_data()

    def init_ui(self):
        self.checkBox.setText('是')
        self.checkBox_send_error_log.clicked.connect(self.set_error_log)

    def show_info(self):
        QMessageBox.information(self, "收集错误信息",
                                "为了更好的解决用户问题，需要收集软件崩溃导致的错误信息，该操作不会上传包括手机号、微信号、昵称等在内的任何信息\n"
                                )

    def set_error_log(self):
        if self.checkBox_send_error_log.isChecked():
            self.label_error_log.setText('开')
            set_SEND_LOG_FLAG(True)
        else:
            self.label_error_log.setText('关')
            set_SEND_LOG_FLAG(False)
        print('SEND_LOG_FLAG:', SEND_LOG_FLAG)

    def read_data(self):
        os.makedirs('./app/data', exist_ok=True)
        stopwords = ['裂开', '苦涩', '叹气', '凋谢', '让我看看', '酷', '奋斗', '疑问', '擦汗', '抠鼻', '鄙视', '勾引',
                     '奸笑', '嘿哈', '捂脸', '机智', '加油', '吃瓜', '尴尬', '炸弹', '旺柴']
        new_words = ['YYDS', '666', '显眼包', '遥遥领先']
        if os.path.exists('./app/data/stopwords.txt'):
            with open('./app/data/stopwords.txt', 'r', encoding='utf-8') as f:
                stopwords = set(f.read().splitlines())
                self.plainTextEdit.setPlainText(' '.join(stopwords))
        else:
            self.plainTextEdit.setPlainText(' '.join(stopwords))
            stopwords = '\n'.join(stopwords)
            with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
                f.write(stopwords)
        if os.path.exists('./app/data/new_words.txt'):
            with open('./app/data/new_words.txt', 'r', encoding='utf-8') as f:
                new_words = set(f.read().splitlines())
                self.plainTextEdit_newword.setPlainText(' '.join(new_words))
        else:
            self.plainTextEdit_newword.setPlainText(' '.join(new_words))
            stopwords = '\n'.join(new_words)
            with open('./app/data/new_words.txt', 'w', encoding='utf-8') as f:
                f.write(stopwords)

    def add_stopwords(self):
        text = self.plainTextEdit.toPlainText()
        stopwords = '\n'.join(text.split())
        with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
            f.write(stopwords)
        QMessageBox.about(self, "添加成功", "停用词添加成功")

    def add_new_words(self):
        text = self.plainTextEdit_newword.toPlainText()
        new_words = '\n'.join(text.split())
        with open('./app/data/new_words.txt', 'w', encoding='utf-8') as f:
            f.write(new_words)
        QMessageBox.about(self, "添加成功", "自定义词添加成功")

    def send_error_log(self):
        self.send_thread = ErrorThread()
        self.send_thread.signal.connect(self.show_resp)
        self.send_thread.start()

    def show_resp(self, message):
        if message.get('code') == 200:
            QMessageBox.about(self, "发送结果", f"日志发送成功\n{message.get('message')}")
        else:
            QMessageBox.about(self, "发送结果", f"{message.get('code')}:{message.get('errmsg')}")


class ErrorThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self, message=''):
        super(ErrorThread, self).__init__()
        if message:
            self.message = message
        else:
            filename = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            file_path = f'{filename}-log.log'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='gbk') as f:
                    self.message = f.read()
            elif os.path.exists(f'./app/log/logs/{filename}-log.log'):
                with open(f'./app/log/logs/{filename}-log.log', 'r', encoding='gbk') as f:
                    self.message = f.read()

    def __del__(self):
        pass

    def send_error_msg(self, message):
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

    def run(self):
        resp_info = self.send_error_msg(self.message)
        self.signal.emit(resp_info)
