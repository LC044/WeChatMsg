import csv
import os

from app.DataBase import msg_db
from app.DataBase.output import ExporterBase


class CSVExporter(ExporterBase):
    def to_csv(self):
        print(f"【开始导出 CSV {self.contact.remark}】")
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}_utf8.csv"
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime', 'Remark', 'NickName', 'Sender']
        messages = msg_db.get_messages(self.contact.wxid, time_range=self.time_range)
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            # writer.writerows(messages)
            for msg in messages:
                other_data = [msg[12].remark, msg[12].nickName, msg[12].wxid] if self.contact.is_chatroom else []
                writer.writerow([*msg[:9], *other_data])
        print(f"【完成导出 CSV {self.contact.remark}】")
        self.okSignal.emit(1)

    def run(self):
        self.to_csv()
