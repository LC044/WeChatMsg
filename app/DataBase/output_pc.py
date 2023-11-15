import os

import numpy as np
import pandas as pd
from PyQt5.QtCore import pyqtSignal


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

    def __init__(self, ta_u, parent=None, type_=DOCX):
        super().__init__(parent)
        self.sec = 2  # 默认1000秒
        self.ta_username = ta_u
        self.msg_id = 0
        self.output_type = type_
        self.total_num = 0

    @log
    def to_csv(self, conRemark, path):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{conRemark}"
        filename = f"{os.path.abspath('.')}/data/聊天记录/{conRemark}/{conRemark}.csv"
        last_timestamp = 1601968667000
        columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        df = pd.DataFrame()
        df["用户名"] = np.array(list(map(lambda x: x[7], messages)))
        df["消息内容"] = np.array(list(map(lambda x: x[8], messages)))
        df["发送时间"] = np.array(list(map(lambda x: time_format(x[6]), messages)))
        df["发送状态"] = np.array(list(map(lambda x: x[3], messages)))
        df["消息类型"] = np.array(list(map(lambda x: x[2], messages)))
        df["isSend"] = np.array(list(map(lambda x: x[4], messages)))
        df["msgId"] = np.array(list(map(lambda x: x[0], messages)))
        df.to_csv(filename)
        # df.to_csv('data.csv')
        print(df)
        self.progressSignal.emit(self.num)

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV:
            # print("线程导出csv")
            self.to_csv(self.ta_username, "path")
