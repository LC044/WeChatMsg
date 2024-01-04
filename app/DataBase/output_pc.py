import csv
import os
import traceback

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog

from app.DataBase.exporter_csv import CSVExporter
from app.DataBase.exporter_docx import DocxExporter
from app.DataBase.exporter_html import HtmlExporter
from app.DataBase.exporter_txt import TxtExporter
from app.DataBase.hard_link import decodeExtraBuf
from .package_msg import PackageMsg
from ..DataBase import media_msg_db, hard_link_db, micro_msg_db, msg_db
from ..log import logger
from ..person import Me
from ..util.image import get_image

os.makedirs('./data/聊天记录', exist_ok=True)


class Output(QThread):
    """
    发送信息线程
    """
    startSignal = pyqtSignal(int)
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1
    CSV = 0
    DOCX = 1
    HTML = 2
    CSV_ALL = 3
    CONTACT_CSV = 4
    TXT = 5

    def __init__(self, contact, type_=DOCX, message_types={}, parent=None):
        super().__init__(parent)
        self.Child0 = None
        self.last_timestamp = 0
        self.message_types = message_types
        self.sec = 2  # 默认1000秒
        self.contact = contact
        self.ta_username = contact.wxid if contact else ''
        self.msg_id = 0
        self.output_type = type_
        self.total_num = 1
        self.num = 0

    def progress(self, value):
        self.progressSignal.emit(value)

    def output_image(self):
        """
        导出全部图片
        @return:
        """
        return

    def output_emoji(self):
        """
        导出全部表情包
        @return:
        """
        return

    def to_csv_all(self):
        """
        导出全部聊天记录到CSV
        @return:
        """
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = QFileDialog.getSaveFileName(None, "save file", os.path.join(os.getcwd(), 'messages.csv'),
                                               "csv files (*.csv);;all files(*.*)")
        if not filename[0]:
            return
        self.startSignal.emit(1)
        filename = filename[0]
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime', 'Remark', 'NickName', 'Sender']

        packagemsg = PackageMsg()
        messages = packagemsg.get_package_message_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def contact_to_csv(self):
        """
        导出联系人到CSV
        @return:
        """
        filename = QFileDialog.getSaveFileName(None, "save file", os.path.join(os.getcwd(), 'contacts.csv'),
                                               "csv files (*.csv);;all files(*.*)")
        if not filename[0]:
            return
        self.startSignal.emit(1)
        filename = filename[0]
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['UserName', 'Alias', 'Type', 'Remark', 'NickName', 'PYInitial', 'RemarkPYInitial', 'smallHeadImgUrl',
                   'bigHeadImgUrl', 'label', 'gender', 'telephone', 'signature', 'country/region', 'province', 'city']
        contacts = micro_msg_db.get_contact()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            # writer.writerows(contacts)
            for contact in contacts:
                detail = decodeExtraBuf(contact[9])
                gender_code = detail.get('gender')
                if gender_code == 0:
                    gender = '未知'
                elif gender_code == 1:
                    gender = '男'
                else:
                    gender = '女'
                writer.writerow([*contact[:9], contact[10], gender,detail.get('telephone'),detail.get('signature'),*detail.get('region')])

        self.okSignal.emit(1)

    def run(self):
        if self.output_type == self.DOCX:
            self.Child = DocxExporter(self.contact, type_=self.output_type, message_types=self.message_types)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()
        elif self.output_type == self.CSV_ALL:
            self.to_csv_all()
        elif self.output_type == self.CONTACT_CSV:
            self.contact_to_csv()
        elif self.output_type == self.TXT:
            self.Child = TxtExporter(self.contact, type_=self.output_type, message_types=self.message_types)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()
        elif self.output_type == self.CSV:
            self.Child = CSVExporter(self.contact, type_=self.output_type, message_types=self.message_types)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()
        elif self.output_type == self.HTML:
            self.Child = HtmlExporter(self.contact, type_=self.output_type, message_types=self.message_types)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.count_finish_num)
            self.Child.start()
            if self.message_types.get(34):
                # 语音消息单独的线程
                self.total_num += 1
                self.output_media = OutputMedia(self.contact)
                self.output_media.okSingal.connect(self.count_finish_num)
                self.output_media.progressSignal.connect(self.progressSignal)
                self.output_media.start()
            if self.message_types.get(47):
                # emoji消息单独的线程
                self.total_num += 1
                self.output_emoji = OutputEmoji(self.contact)
                self.output_emoji.okSingal.connect(self.count_finish_num)
                self.output_emoji.progressSignal.connect(self.progressSignal)
                self.output_emoji.start()
            if self.message_types.get(3):
                # 图片消息单独的线程
                self.total_num += 1
                self.output_image = OutputImage(self.contact)
                self.output_image.okSingal.connect(self.count_finish_num)
                self.output_image.progressSignal.connect(self.progressSignal)
                self.output_image.start()

    def count_finish_num(self, num):
        """
        记录子线程完成个数
        @param num:
        @return:
        """
        self.num += 1
        if self.num == self.total_num:
            # 所有子线程都完成之后就发送完成信号
            self.okSignal.emit(1)

    def cancel(self):
        self.requestInterruption()


class OutputMedia(QThread):
    """
    导出语音消息
    """
    okSingal = pyqtSignal(int)
    progressSignal = pyqtSignal(int)

    def __init__(self, contact):
        super().__init__()
        self.contact = contact

    def run(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        messages = msg_db.get_messages_by_type(self.contact.wxid, 34)
        for message in messages:
            is_send = message[4]
            msgSvrId = message[9]
            try:
                audio_path = media_msg_db.get_audio(msgSvrId, output_path=origin_docx_path + "/voice")
            except:
                logger.error(traceback.format_exc())
            finally:
                self.progressSignal.emit(1)
        self.okSingal.emit(34)


class OutputEmoji(QThread):
    """
    导出表情包
    """
    okSingal = pyqtSignal(int)
    progressSignal = pyqtSignal(int)

    def __init__(self, contact):
        super().__init__()
        self.contact = contact

    def run(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        messages = msg_db.get_messages_by_type(self.contact.wxid, 47)
        for message in messages:
            str_content = message[7]
            try:
                pass
                # emoji_path = get_emoji(str_content, thumb=True, output_path=origin_docx_path + '/emoji')
            except:
                logger.error(traceback.format_exc())
            finally:
                self.progressSignal.emit(1)
        self.okSingal.emit(47)


class OutputImage(QThread):
    """
    导出图片
    """
    okSingal = pyqtSignal(int)
    progressSignal = pyqtSignal(int)

    def __init__(self, contact):
        super().__init__()
        self.contact = contact
        self.child_thread_num = 2
        self.child_threads = [0] * (self.child_thread_num + 1)
        self.num = 0

    def count1(self, num):
        self.num += 1
        print('图片导出完成一个')
        if self.num == self.child_thread_num:
            self.okSingal.emit(47)
            print('图片导出完成')

    def run(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        messages = msg_db.get_messages_by_type(self.contact.wxid, 3)
        for message in messages:
            str_content = message[7]
            BytesExtra = message[10]
            timestamp = message[5]
            try:
                image_path = hard_link_db.get_image(str_content, BytesExtra, thumb=False)
                if not os.path.exists(os.path.join(Me().wx_dir, image_path)):
                    image_thumb_path = hard_link_db.get_image(str_content, BytesExtra, thumb=True)
                    if not os.path.exists(os.path.join(Me().wx_dir, image_thumb_path)):
                        continue
                    image_path = image_thumb_path
                image_path = get_image(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
                try:
                    os.utime(origin_docx_path + image_path[1:], (timestamp, timestamp))
                except:
                    pass
            except:
                logger.error(traceback.format_exc())
            finally:
                self.progressSignal.emit(1)
        self.okSingal.emit(47)


class OutputImageChild(QThread):
    okSingal = pyqtSignal(int)
    progressSignal = pyqtSignal(int)

    def __init__(self, contact, messages):
        super().__init__()
        self.contact = contact
        self.messages = messages

    def run(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        for message in self.messages:
            str_content = message[7]
            BytesExtra = message[10]
            timestamp = message[5]
            try:
                image_path = hard_link_db.get_image(str_content, BytesExtra, thumb=False)
                if not os.path.exists(os.path.join(Me().wx_dir, image_path)):
                    image_thumb_path = hard_link_db.get_image(str_content, BytesExtra, thumb=True)
                    if not os.path.exists(os.path.join(Me().wx_dir, image_thumb_path)):
                        continue
                    image_path = image_thumb_path
                image_path = get_image(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
                try:
                    os.utime(origin_docx_path + image_path[1:], (timestamp, timestamp))
                except:
                    pass
            except:
                logger.error(traceback.format_exc())
            finally:
                self.progressSignal.emit(1)
        self.okSingal.emit(47)
        print('图片子线程完成')


if __name__ == "__main__":
    pass
