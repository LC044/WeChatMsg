import csv
import os

from app.DataBase import msg_db
from app.person import Me
from app.util.exporter.exporter import ExporterBase
from app.config import OUTPUT_DIR


class CSVExporter(ExporterBase):
    def to_csv(self):
        print(f"【开始导出 CSV {self.contact.remark}】")
        origin_path = os.path.join(os.getcwd(), OUTPUT_DIR, '聊天记录', self.contact.remark)
        os.makedirs(origin_path, exist_ok=True)
        filename = os.path.join(origin_path,f"{self.contact.remark}_utf8.csv")
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
                if self.contact.is_chatroom:
                    other_data = [msg[13].remark, msg[13].nickName, msg[13].wxid]
                else:
                    is_send = msg[4]
                    Remark = Me().remark if is_send else self.contact.remark
                    nickname = Me().nickName if is_send else self.contact.nickName
                    wxid = Me().wxid if is_send else self.contact.wxid
                    other_data = [Remark,nickname,wxid]
                writer.writerow([*msg[:9], *other_data])
        print(f"【完成导出 CSV {self.contact.remark}】")
        self.okSignal.emit(1)

    def run(self):
        self.to_csv()
