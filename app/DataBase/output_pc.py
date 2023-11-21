import os

import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread

from . import msg
from ..log import log

if not os.path.exists('./data/聊天记录'):
    os.mkdir('./data/聊天记录')


class Output(QThread):
    """
    发送信息线程
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1
    CSV = 0
    DOCX = 1
    HTML = 2

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.sec = 2  # 默认1000秒
        self.contact = contact
        self.ta_username = contact.wxid
        self.msg_id = 0
        self.output_type = type_
        self.total_num = 0
        self.num = 0

    @log
    def to_csv(self, conRemark, path):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        if not os.path.exists(origin_docx_path):
            os.mkdir(origin_docx_path)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg.get_messages(self.contact.wxid)
        # print()
        df = pd.DataFrame(
            data=messages,
            columns=columns,
        )
        df.to_csv(filename, encoding='utf-8')
        self.okSignal.emit('ok')

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV:
            # print("线程导出csv")
            self.to_csv(self.ta_username, "path")
