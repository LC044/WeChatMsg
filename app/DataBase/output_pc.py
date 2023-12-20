import csv
import html
import os
from re import findall
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog
# from eyed3 import load

from . import msg_db, micro_msg_db
from .package_msg import PackageMsg
from ..DataBase import hard_link_db
from ..DataBase import media_msg_db
from ..person import MePC
from ..util import path
import shutil

from ..util.compress_content import parser_reply
from ..util.emoji import get_emoji

os.makedirs('./data/聊天记录', exist_ok=True)


def makedirs(path):
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, 'image'), exist_ok=True)
    os.makedirs(os.path.join(path, 'emoji'), exist_ok=True)
    os.makedirs(os.path.join(path, 'video'), exist_ok=True)
    os.makedirs(os.path.join(path, 'voice'), exist_ok=True)
    os.makedirs(os.path.join(path, 'file'), exist_ok=True)
    os.makedirs(os.path.join(path, 'avatar'), exist_ok=True)


def escape_js_and_html(input_str):
    # 转义HTML特殊字符
    html_escaped = html.escape(input_str, quote=False)

    # 手动处理JavaScript转义字符
    js_escaped = (
        html_escaped
        .replace("\\", "\\\\")
        .replace("'", r"\'")
        .replace('"', r'\"')
        .replace("\n", r'\n')
        .replace("\r", r'\r')
        .replace("\t", r'\t')
    )

    return js_escaped


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
        self.total_num = 0
        self.num = 0

    def progress(self, value):
        self.progressSignal.emit(value)

    def to_csv_all(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = QFileDialog.getSaveFileName(None, "save file", os.path.join(os.getcwd(), 'messages.csv'),
                                               "csv files (*.csv);;all files(*.*)")
        if not filename[0]:
            return
        filename = filename[0]
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime', 'Remark', 'NickName', 'Sender']

        packagemsg = PackageMsg()
        messages = packagemsg.get_package_message_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def contact_to_csv(self):
        filename = QFileDialog.getSaveFileName(None, "save file", os.path.join(os.getcwd(), 'contacts.csv'),
                                               "csv files (*.csv);;all files(*.*)")
        if not filename[0]:
            return
        filename = filename[0]
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['UserName', 'Alias', 'Type', 'Remark', 'NickName', 'PYInitial', 'RemarkPYInitial', 'smallHeadImgUrl',
                   'bigHeadImgUrl']
        contacts = micro_msg_db.get_contact()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(contacts)
        self.okSignal.emit(1)

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV_ALL:
            self.to_csv_all()
        elif self.output_type == self.CONTACT_CSV:
            self.contact_to_csv()
        else:
            self.Child = ChildThread(self.contact, type_=self.output_type, message_types=self.message_types)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()

    def cancel(self):
        self.requestInterruption()


def modify_audio_metadata(audiofile, new_artist): # 修改音频元数据中的“创作者”标签
    return
    audiofile = load(audiofile)
    
    # 检查文件是否有标签
    if audiofile.tag is None:
        audiofile.initTag()

    # 修改艺术家名称
    audiofile.tag.artist = new_artist
    audiofile.tag.save()


class ChildThread(QThread):
    """
        子线程，用于导出部分聊天记录
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1
    CSV = 0
    DOCX = 1
    HTML = 2

    def __init__(self, contact, type_=DOCX, message_types={}, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.message_types = message_types
        self.last_timestamp = 0
        self.sec = 2  # 默认1000秒
        self.msg_id = 0
        self.output_type = type_

    def is_5_min(self, timestamp):
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp
            return True
        return False

    def text(self, doc, message):
        type_ = message[2]
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            str_content = escape_js_and_html(str_content)
            if self.is_5_min(timestamp):
                doc.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            emojiText = findall(r"(\[.+?\])", str_content)
            for emoji_text in emojiText:
                if emoji_text in emoji:
                    str_content = str_content.replace(emoji_text, emoji[emoji_text])
            doc.write(
                f'''{{ type:{1}, text: '{str_content}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
            )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n{str_content}\n\n'''
            )

    def image(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        type_ = message[2]
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        BytesExtra = message[10]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            str_content = escape_js_and_html(str_content)
            image_path = hard_link_db.get_image(str_content, BytesExtra, thumb=False)
            image_thumb_path = hard_link_db.get_image(str_content, BytesExtra, thumb=True)
            if not os.path.exists(os.path.join(MePC().wx_dir, image_path)):
                image_path = None
            if not os.path.exists(os.path.join(MePC().wx_dir, image_thumb_path)):
                image_thumb_path = None
            if image_path is None and image_thumb_path is not None:
                image_path = image_thumb_path
            if image_path is None and image_thumb_path is None:
                return
            image_path = path.get_relative_path(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
            image_path = image_path.replace('/', '\\')
            try:
                os.utime(origin_docx_path + image_path[1:], (timestamp, timestamp))
            except:
                print("网络图片",image_path)
                pass
            image_path = image_path.replace('\\', '/')
            # print(f"tohtml:---{image_path}")
            if self.is_5_min(timestamp):
                doc.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            doc.write(
                f'''{{ type:{type_}, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
            )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n[图片]\n\n'''
            )

    def audio(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        msgSvrId = message[9]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            try:
                audio_path = media_msg_db.get_audio(msgSvrId, output_path=origin_docx_path + "/voice")
                audio_path = audio_path.replace('/', '\\')
                modify_audio_metadata(audio_path, displayname)
                os.utime(audio_path, (timestamp, timestamp))
                audio_path = audio_path.replace('\\', '/')
                audio_path = "./voice/" + os.path.basename(audio_path)
                voice_to_text = escape_js_and_html(media_msg_db.get_audio_text(str_content))
            except:
                return
            if self.is_5_min(timestamp):
                doc.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            doc.write(
                f'''{{ type:34, text:'{audio_path}',is_send:{is_send},avatar_path:'{avatar}',voice_to_text:'{voice_to_text}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
            )
        if self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n[语音]\n\n'''
            )

    def emoji(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            emoji_path = get_emoji(str_content, thumb=True, output_path=origin_docx_path + '/emoji')
            if emoji_path == "":
                shutil.copy(f"{os.path.abspath('.')}/app/resources/icons/404.png", origin_docx_path + '/emoji/404.png')
                emoji_path = "./emoji/404.png"
            else:
                emoji_path = './emoji/' + os.path.basename(emoji_path)
            if self.is_5_min(timestamp):
                doc.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            doc.write(
                f'''{{ type:{3}, text: '{emoji_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
            )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n[表情包]\n\n'''
            )

    def wx_file(self, doc, isSend, content, status):
        return

    def retract_message(self, doc, isSend, content, status):
        return

    def refermsg(self, doc, message):
        """
        处理回复消息
        @param doc:
        @param message:
        @return:
        """
        type_ = message[2]
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        avatar = 'myhead.png' if is_send else 'tahead.png'
        content = parser_reply(message[11])
        refer_msg = content.get('refer')
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            contentText = escape_js_and_html(content.get('title'))
            emojiText = findall(r"(\[.+?\])", contentText)
            for emoji_text in emojiText:
                if emoji_text in emoji:
                    contentText = contentText.replace(emoji_text, emoji[emoji_text])
            if refer_msg:
                referText = f"{escape_js_and_html(refer_msg.get('displayname'))}：{escape_js_and_html(refer_msg.get('content'))}"
                emojiText = findall(r"(\[.+?\])", referText)
                for emoji_text in emojiText:
                    if emoji_text in emoji:
                        referText = referText.replace(emoji_text, emoji[emoji_text])
                doc.write(
                    f'''{{ type:49, text: '{contentText}',is_send:{is_send},sub_type:{content.get('type')},refer_text: '{referText}',avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            else:
                doc.write(
                    f'''{{ type:49, text: '{contentText}',is_send:{is_send},sub_type:{content.get('type')},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            if refer_msg:
                doc.write(
                    f'''{str_time} {name}\n{content.get('title')}\n引用:{refer_msg.get('displayname')}:{refer_msg.get('content')}\n\n'''
                )
            else:
                doc.write(
                    f'''{str_time} {name}\n{content.get('title')}\n引用:未知\n\n'''
                )

    def system_msg(self, doc, message):
        str_content = message[7]
        is_send = message[4]
        str_time = message[8]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        str_content = str_content.replace('<![CDATA[', "").replace(' <a href="weixin://revoke_edit_click">重新编辑</a>]]>', "")
        res = findall('(</{0,1}(img|revo|_wc_cus|a).*?>)', str_content)
        for xmlstr, b in res:
            str_content = str_content.replace(xmlstr, "")
        str_content = escape_js_and_html(str_content)
        if self.output_type == Output.HTML:
            doc.write(
                f'''{{ type:0, text: '{str_content}',is_send:{is_send},avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:''}},'''
            )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n{str_content}\n\n'''
            )

    def video(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        type_ = message[2]
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        BytesExtra = message[10]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        if is_chatroom:
            avatar = f"./avatar/{message[12].wxid}.png"
        else:
            avatar = f"./avatar/{MePC().wxid if is_send else self.contact.wxid}.png"
        if is_chatroom:
            if is_send:
                displayname = MePC().name
            else:
                displayname = message[12].remark
        else:
            displayname = MePC().name if is_send else self.contact.remark
        displayname = escape_js_and_html(displayname)
        if self.output_type == Output.HTML:
            video_path = hard_link_db.get_video(str_content, BytesExtra, thumb=False)
            image_path = hard_link_db.get_video(str_content, BytesExtra, thumb=True)
            if video_path is None and image_path is not None:
                image_path = path.get_relative_path(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
                try:
                    # todo 网络图片问题
                    print(origin_docx_path + image_path[1:])
                    os.utime(origin_docx_path + image_path[1:], (timestamp, timestamp))
                    image_path = image_path.replace('\\', '/')
                    # print(f"tohtml:---{image_path}")
                    if self.is_5_min(timestamp):
                        doc.write(
                            f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                        )
                    doc.write(
                        f'''{{ type:3, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                    )
                except:
                    doc.write(
                        f'''{{ type:1, text: '视频丢失',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                    )
                return
            if video_path is None and image_path is None:
                return
            video_path = f'{MePC().wx_dir}/{video_path}'
            if os.path.exists(video_path):
                new_path = origin_docx_path + '/video/' + os.path.basename(video_path)
                if not os.path.exists(new_path):
                    shutil.copy(video_path, os.path.join(origin_docx_path, 'video'))
                os.utime(new_path, (timestamp, timestamp))
                video_path = f'./video/{os.path.basename(video_path)}'
            video_path = video_path.replace('\\', '/')
            if self.is_5_min(timestamp):
                doc.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
                )
            doc.write(
                f'''{{ type:{type_}, text: '{video_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{displayname}'}},'''
            )
        elif self.output_type == Output.TXT:
            name = '你' if is_send else self.contact.remark
            doc.write(
                f'''{str_time} {name}\n[视频]\n\n'''
            )

    def to_csv(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}_utf8.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg_db.get_messages(self.contact.wxid)
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        # with open(filename, mode='r', newline='', encoding='utf-8') as file:
        #     content = file.read()
        # filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}_gbk.csv"
        # with open(filename, mode='w', newline='', encoding='gbk') as file:
        #     file.write(content.encode('utf-8', errors='ignore').decode('gbk', errors='ignore'))
        self.okSignal.emit('ok')

    def to_html_(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        makedirs(origin_docx_path)
        if self.contact.is_chatroom:
            packagemsg = PackageMsg()
            messages = packagemsg.get_package_message_by_wxid(self.contact.wxid)
        else:
            messages = msg_db.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        f = open(filename, 'w', encoding='utf-8')
        f.write(html_head.replace("<title>Chat Records</title>", f"<title>{self.contact.remark}</title>"))
        MePC().avatar.save(os.path.join(f"{origin_docx_path}/avatar/{MePC().wxid}.png"))
        if self.contact.is_chatroom:
            for message in messages:
                if message[4]: # is_send
                    continue
                try:
                    chatroom_avatar_path = f"{origin_docx_path}/avatar/{message[12].wxid}.png"
                    if not os.path.exists(chatroom_avatar_path):
                        message[12].avatar.save(chatroom_avatar_path)
                except:
                    pass
        else:
            self.contact.avatar.save(os.path.join(f"{origin_docx_path}/avatar/{self.contact.wxid}.png"))
        self.rangeSignal.emit(len(messages))
        total_steps = len(messages)
        for index, message in enumerate(messages):
            type_ = message[2]
            sub_type = message[3]
            self.progressSignal.emit(int((index + 1) / total_steps * 100))
            if type_ == 1 and self.message_types.get(type_):
                self.text(f, message)
            elif type_ == 3 and self.message_types.get(type_):
                self.image(f, message)
            elif type_ == 34 and self.message_types.get(type_):
                self.audio(f, message)
            elif type_ == 43 and self.message_types.get(type_):
                self.video(f, message)
            elif type_ == 47 and self.message_types.get(type_):
                self.emoji(f, message)
            elif type_ == 10000 and self.message_types.get(type_):
                self.system_msg(f, message)
            elif type_ == 49 and sub_type == 57 and self.message_types.get(1):
                self.refermsg(f, message)
        f.write(html_end)
        f.close()
        self.okSignal.emit(1)

    def to_txt(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.txt"
        messages = msg_db.get_messages(self.contact.wxid)
        total_steps = len(messages)
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            for index, message in enumerate(messages):
                type_ = message[2]
                sub_type = message[3]
                self.progressSignal.emit(int((index + 1) / total_steps * 100))
                if type_ == 1 and self.message_types.get(type_):
                    self.text(f, message)
                elif type_ == 3 and self.message_types.get(type_):
                    self.image(f, message)
                elif type_ == 34 and self.message_types.get(type_):
                    self.audio(f, message)
                elif type_ == 43 and self.message_types.get(type_):
                    self.video(f, message)
                elif type_ == 47 and self.message_types.get(type_):
                    self.emoji(f, message)
                elif type_ == 10000 and self.message_types.get(type_):
                    self.system_msg(f, message)
                elif type_ == 49 and sub_type == 57:
                    self.refermsg(f, message)
        self.okSignal.emit(1)

    def run(self):
        if self.output_type == Output.DOCX:
            return
        elif self.output_type == Output.CSV:
            self.to_csv()
        elif self.output_type == Output.HTML:
            self.to_html_()
        elif self.output_type == Output.CSV_ALL:
            self.to_csv_all()
        elif self.output_type == Output.TXT:
            self.to_txt()

    def cancel(self):
        self.requestInterruption()


emoji = {
    '[微笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_1@2x.png" id="微笑" class="emoji_img">',
    '[撇嘴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_2@2x.png" id="撇嘴" class="emoji_img">',
    '[色]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_3@2x.png" id="色" class="emoji_img">',
    '[发呆]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_4@2x.png" id="发呆" class="emoji_img">',
    '[得意]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_5@2x.png" id="得意" class="emoji_img">',
    '[流泪]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_6@2x.png" id="流泪" class="emoji_img">',
    '[害羞]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_7@2x.png" id="害羞" class="emoji_img">',
    '[闭嘴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_8@2x.png" id="闭嘴" class="emoji_img">',
    '[睡]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_9@2x.png" id="睡" class="emoji_img">',
    '[大哭]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_10@2x.png" id="大哭" class="emoji_img">',
    '[尴尬]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_11@2x.png" id="尴尬" class="emoji_img">',
    '[发怒]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_12@2x.png" id="发怒" class="emoji_img">',
    '[调皮]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_13@2x.png" id="调皮" class="emoji_img">',
    '[呲牙]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_14@2x.png" id="呲牙" class="emoji_img">',
    '[惊讶]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_15@2x.png" id="惊讶" class="emoji_img">',
    '[难过]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_16@2x.png" id="难过" class="emoji_img">',
    '[抓狂]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_19@2x.png" id="抓狂" class="emoji_img">',
    '[吐]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_20@2x.png" id="吐" class="emoji_img">',
    '[偷笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_21@2x.png" id="偷笑" class="emoji_img">',
    '[愉快]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_22@2x.png" id="愉快" class="emoji_img">',
    '[白眼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_23@2x.png" id="白 眼" class="emoji_img">',
    '[傲慢]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_24@2x.png" id="傲慢" class="emoji_img">',
    '[困]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_26@2x.png" id="困" class="emoji_img">',
    '[惊恐]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_27@2x.png" id="惊恐" class="emoji_img">',
    '[憨笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_29@2x.png" id="憨笑" class="emoji_img">',
    '[悠闲]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_30@2x.png" id="悠闲" class="emoji_img">',
    '[咒骂]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_32@2x.png" id="咒骂" class="emoji_img">',
    '[疑问]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_33@2x.png" id="疑问" class="emoji_img">',
    '[嘘]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_34@2x.png" id="嘘" class="emoji_img">',
    '[晕]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_35@2x.png" id="晕" class="emoji_img">',
    '[衰]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_37@2x.png" id="衰" class="emoji_img">',
    '[骷髅]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_38@2x.png" id="骷髅" class="emoji_img">',
    '[敲打]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_39@2x.png" id="敲打" class="emoji_img">',
    '[再见]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_40@2x.png" id="再见" class="emoji_img">',
    '[擦汗]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_41@2x.png" id="擦汗" class="emoji_img">',
    '[抠鼻]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_42@2x.png" id="抠鼻" class="emoji_img">',
    '[鼓掌]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_43@2x.png" id="鼓掌" class="emoji_img">',
    '[坏笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_45@2x.png" id="坏笑" class="emoji_img">',
    '[右哼哼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_47@2x.png" id="右哼哼" class="emoji_img">',
    '[鄙视]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_49@2x.png" id="鄙视" class="emoji_img">',
    '[委屈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_50@2x.png" id="委屈" class="emoji_img">',
    '[快哭了]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_51@2x.png" id="快哭了" class="emoji_img">',
    '[阴险]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_52@2x.png" id="阴险" class="emoji_img">',
    '[亲亲]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_53@2x.png" id="亲亲" class="emoji_img">',
    '[可怜]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_55@2x.png" id="可怜" class="emoji_img">',
    '[Whimper]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_55@2x.png" id="可怜" class="emoji_img">',
    '[笑脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Happy.png" id="笑脸" class="emoji_img">',
    '[生病]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sick.png" id="生病" class="emoji_img">',
    '[脸红]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Flushed.png" id="脸红" class="emoji_img">',
    '[破涕为笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Lol.png" id="破涕为笑" class="emoji_img">',
    '[恐惧]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Terror.png" id="恐惧" class="emoji_img">',
    '[失望]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/LetDown.png" id="失望" class="emoji_img">',
    '[无语]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Duh.png" id="无语" class="emoji_img">',
    '[嘿哈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_04.png" id="嘿哈" class="emoji_img">',
    '[捂脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_05.png" id="捂脸" class="emoji_img">',
    '[奸笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_02.png" id="奸笑" class="emoji_img">',
    '[机智]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_06.png" id="机智" class="emoji_img">',
    '[皱眉]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_12.png" id="皱眉" class="emoji_img">',
    '[耶]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_11.png" id="耶" class="emoji_img">',
    '[吃瓜]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Watermelon.png" id="吃瓜" class="emoji_img">',
    '[加油]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Addoil.png" id="加油" class="emoji_img">',
    '[汗]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sweat.png" id="汗" class="emoji_img">',
    '[天啊]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Shocked.png" id="天啊" class="emoji_img">',
    '[Emm]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Cold.png" id="Emm" class="emoji_img">',
    '[社会社会]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Social.png" id="社会社会" class="emoji_img">',
    '[旺柴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Yellowdog.png" id="旺柴" class="emoji_img">',
    '[好的]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/NoProb.png" id="好的" class="emoji_img">',
    '[打脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Slap.png" id="打脸" class="emoji_img">',
    '[哇]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Wow.png" id="哇" class="emoji_img">',
    '[翻白眼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Boring.png" id="翻白眼" class="emoji_img">',
    '[666]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/666.png" id="666" class="emoji_img">',
    '[让我看看]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/LetMeSee.png" id="让我看看" class="emoji_img">',
    '[叹气]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sigh.png" id="叹气" class="emoji_img">',
    '[苦涩]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Hurt.png" id="苦涩" class="emoji_img">',
    '[裂开]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Broken.png" id="裂开" class="emoji_img">',
    '[嘴唇]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_66@2x.png" id="嘴唇" class="emoji_img">',
    '[爱心]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_67@2x.png" id="爱心" class="emoji_img">',
    '[心碎]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_68@2x.png" id="心碎" class="emoji_img">',
    '[拥抱]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_79@2x.png" id="拥抱" class="emoji_img">',
    '[强]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_80@2x.png" id="强" class="emoji_img">',
    '[弱]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_81@2x.png" id="弱" class="emoji_img">',
    '[握手]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_82@2x.png" id="握手" class="emoji_img">',
    '[胜利]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_83@2x.png" id="胜利" class="emoji_img">',
    '[抱拳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_84@2x.png" id="抱拳" class="emoji_img">',
    '[勾引]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_85@2x.png" id="勾引" class="emoji_img">',
    '[拳头]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_86@2x.png" id="拳头" class="emoji_img">',
    '[OK]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_90@2x.png" id="OK" class="emoji_img">',
    '[合十]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Worship.png" id="合十" class="emoji_img">',
    '[啤酒]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_58@2x.png" id="啤酒" class="emoji_img">',
    '[咖啡]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_61@2x.png" id="咖啡" class="emoji_img">',
    '[蛋糕]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_69@2x.png" id="蛋糕" class="emoji_img">',
    '[玫瑰]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_64@2x.png" id="玫 瑰" class="emoji_img">',
    '[凋谢]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_65@2x.png" id="凋谢" class="emoji_img">',
    '[菜刀]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_56@2x.png" id="菜刀" class="emoji_img">',
    '[炸弹]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_71@2x.png" id="炸弹" class="emoji_img">',
    '[便便]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_75@2x.png" id="便便" class="emoji_img">',
    '[月亮]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_76@2x.png" id="月亮" class="emoji_img">',
    '[太阳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_77@2x.png" id="太阳" class="emoji_img">',
    '[庆 祝]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Party.png" id="庆祝" class="emoji_img">',
    '[礼物]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_78@2x.png" id="礼物" class="emoji_img">',
    '[红包]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_09.png" id="红包" class="emoji_img">',
    '[發]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_16.png" id="發" class="emoji_img">',
    '[福]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_15.png" id="福" class="emoji_img">',
    '[烟花]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Fireworks.png" id="烟花" class="emoji_img">',
    '[爆竹]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Firecracker.png" id="爆竹" class="emoji_img">',
    '[猪头]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_63@2x.png" id="猪头" class="emoji_img">',
    '[跳跳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_93@2x.png" id="跳跳" class="emoji_img">',
    '[发抖]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_94@2x.png" id="发抖" class="emoji_img">',
    '[转圈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_96@2x.png" id="转圈" class="emoji_img">'}
html_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Records</title>
    <style>
*{
    padding: 0;
    margin: 0;
}
body{
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal {
    display: none;
    position: fixed;
    z-index: 9999;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
}

.modal-image {
    display: block;
    max-width: 90%;
    max-height: 90%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.container{
    height: 99%;
    width: 900px;
    border-radius: 4px;
    border: 0.5px solid #e0e0e0;
    background-color: #f5f5f5;
    display: flex;
    flex-flow: column;
    overflow: hidden;
}
.content{
    width: calc(100% - 40px);
    padding: 20px;
    overflow-y: scroll;
    flex: 1;
}
.content:hover::-webkit-scrollbar-thumb{
    background:rgba(0,0,0,0.1);
}
.bubble{
    max-width: 400px;
    padding: 10px;
    border-radius: 5px;
    position: relative;
    color: #000;
    word-wrap:break-word;
    word-break:normal;
}
.chat-refer {
    margin-top: 5px;
    max-width: 400px;
    padding: 9px;
    border-radius: 5px;
    position: relative;
    color: #000;
    background-color: #e8e8e8;
    word-wrap:break-word;
    word-break:normal;
}
.chat-refer-right {
    margin-right: 15px;
}
.chat-refer-left{
    margin-left: 15px;
}
.item-left .bubble{
    margin-left: 15px;
    background-color: #fff;
}
.item-left .bubble:before{
    content: "";
    position: absolute;
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-top: 10px solid transparent;
    border-right: 10px solid #fff;
    border-bottom: 10px solid transparent;
    left: -20px;
}
.item-right .bubble{
    margin-right: 15px;
    background-color: #9eea6a;
}
.item-right .bubble:before{
    content: "";
    position: absolute;
    width: 0;
    height: 0;
    border-left: 10px solid #9eea6a;
    border-top: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid transparent;
    right: -20px;
}
.item {
    white-space: pre-wrap;
    margin-top: 15px;
    display: flex;
    width: 100%;
}
.item-refer{
    margin-top: 4px;
}
.item.item-right{
    justify-content: flex-end;
}
.item.item-center{
    justify-content: center;
}
.item.item-center span{
    font-size: 12px;
    padding: 2px 4px;
    color: #fff;
    background-color: #dadada;
    border-radius: 3px;
    -moz-user-select:none; /*火狐*/
    -webkit-user-select:none; /*webkit浏览器*/
    -ms-user-select:none; /*IE10*/
    -khtml-user-select:none; /*早期浏览器*/
    user-select:none;
}

.content-wrapper {
    display: flex;
    flex-direction: column;
}

.content-wrapper-left {
    align-items: baseline;
}

.content-wrapper-right {
    align-items: flex-end;
}

.displayname {
    margin-left: 13px;
    margin-left: 13px;
    font-size: 13px;
    margin-bottom: 5px;
    color: darkgray;
}

.chat-image img{
    margin-right: 18px;
    margin-left: 18px;
    max-width: 300px;
    max-height: auto;
}
.avatar img{
    width: 42px;
    height: 42px;
    border-radius: 50%;
}
.chat-video video{
    margin-right: 18px;
    margin-left: 18px;
    max-width: 350px;
}
.chat-audio{
    max-width: 400px;
}
audio{
    margin-left: 9px;
    margin-right: 9px;
}
.input-area{
    border-top:0.5px solid #e0e0e0;
    height: 150px;
    display: flex;
    flex-flow: column;
    background-color: #fff;
}
textarea{
    flex: 1;
    padding: 5px;
    font-size: 14px;
    border: none;
    cursor: pointer;
    overflow-y: auto;
    overflow-x: hidden;
    outline:none;
    resize:none;
}
.button-area{
    display: flex;
    height: 40px;
    margin-right: 10px;
    line-height: 40px;
    padding: 5px;
    justify-content: flex-end;
}
.button-area button{
    width: 80px;
    border: none;
    outline: none;
    border-radius: 4px;
    float: right;
    cursor: pointer;
}

/* 设置滚动条的样式 */
::-webkit-scrollbar {
    width:10px;
}
/* 滚动槽 */
::-webkit-scrollbar-track {
    -webkit-box-shadow:inset006pxrgba(0,0,0,0.3);
    border-radius:8px;
}
/* 滚动条滑块 */
::-webkit-scrollbar-thumb {
    border-radius:10px;
    background:rgba(0,0,0,0);
    -webkit-box-shadow:inset006pxrgba(0,0,0,0.5);
}

.pagination-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
    margin-left: 20px; /* 新增的左边距 */
}

.button-row,
.jump-row,
#paginationInfo {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}

button {
    padding: 10px 25px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 0 14px;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #2980b9;
}

input {
    padding: 8px;
    width: 120px;
    box-sizing: border-box;
    margin-right: 0px;
    margin-left: 15px;
}

button,
input {
    font-size: 14px;
}

#paginationInfo {
    color: #555;
    font-size: 14px;
}

.emoji_img {
    width: 22px;
    height: 22px;
    vertical-align: middle;
    margin-top: -4.4px;
}

  </style>
</head>
<body>
<div class="container">
    <div class="content" id="chat-container">
        <div class="item item-center"><span>昨天 12:35</span></div>
        <div class="item item-center"><span>你已添加了凡繁烦，现在可以开始聊天了。</span></div>
        <div class="item item-left">
            <div class="avatar">
                <img src="https://dss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=25668084,2889217189&fm=26&gp=0.jpg" />
            </div>
            <div class="bubble bubble-left">您好,我在武汉，你可以直接送过来吗，我有时间的话，可以自己过去拿<br/>！！！<br/>123
            </div>
        </div>

        <div class="item item-right">
            <div class="bubble bubble-right">hello<br/>你好呀</div>
            <div class="avatar">
                <img src="https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=3313909130,2406410525&fm=15&gp=0.jpg" />
            </div>
        </div>
        <div class="item item-center">
            <span>昨天 13:15</span>
        </div>
    </div>
</div>
<div></div>
<div id="modal" class="modal" onclick="hideModal()">
    <img id="modal-image" class="modal-image">
</div>
<div class="pagination-container">
    <div class="button-row">
        <button onclick="prevPage()">上一页</button>
        <button onclick="nextPage()">下一页</button>
    </div>
    <div class="jump-row">
        <input type="number" id="gotoPageInput" onkeydown="checkEnter(event)" placeholder="跳转到第几页">
        <button onclick="gotoPage()">跳转</button>
    </div>
    <div id="paginationInfo"></div>
</div>
<script>
    const chatContainer = document.getElementById('chat-container');
    // Sample chat messages (replace this with your actual data)
    const chatMessages = [
        '''
html_end = '''
    ];
    function checkEnter(event) {
        if (event.keyCode === 13) {
            gotoPage();
        }
    }

    const itemsPerPage = 100; // 每页显示的元素个数
    let currentPage = 1; // 当前页

    function renderPage(page) {
        const container = document.getElementById('chat-container');
        container.innerHTML = ''; // 清空容器

        // 计算当前页应该显示的元素范围
        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        console.log(page);

        // 生成各类标签的函数
        function messageBubble(message, side) {
            const messageBubbleTag = document.createElement('div');
            messageBubbleTag.className = `bubble bubble-${side}`;
            messageBubbleTag.innerHTML = message.text;
            return messageBubbleTag;
        }
        function displayNameBox(message) {
            const displayName = document.createElement('div');
            displayName.className = "displayname";
            displayName.innerHTML = message.displayname;
            return displayName;
        }
        function avatarBox(message) {
            const avatarTag = document.createElement('div');
            avatarTag.className = "avatar";
            avatarTag.innerHTML = `<img src="${message.avatar_path}" />`
            return avatarTag;
        }
        function messageImgBox(message) {
            const messageImgTag = document.createElement('div');
            messageImgTag.className = `chat-image`;
            messageImgTag.innerHTML = `<img src="${message.text}" onclick="showModal(this)"/>`;
            return messageImgTag;
        }
        function messageVideoBox(message) {
            const messageVideoTag = document.createElement('div');
            messageVideoTag.className = `chat-video`;
            messageVideoTag.innerHTML = `<video src="${message.text}" controls />`;
            return messageVideoTag;
        }
        function messageElementReferText(message, side) {
            const messageElementRefer = document.createElement('div');
            messageElementRefer.className = `chat-refer chat-refer-${side}`;
            messageElementRefer.innerHTML = message.refer_text;
            return messageElementRefer;
        }
        function messageVoiceToTextBubble(message, side) {
            const messageVoiceToTextTag = document.createElement('div');
            messageVoiceToTextTag.className = `bubble bubble-${side}`;
            messageVoiceToTextTag.innerHTML = message.voice_to_text;
            return messageVoiceToTextTag;
        }
        function messageAudioBox(message) {
            const messageAudioTag = document.createElement('div');
            messageAudioTag.className = `chat-audio`;
            messageAudioTag.innerHTML = `<audio src="${message.text}" controls></audio>`;
            return messageAudioTag;
        }
        
            // 从数据列表中取出对应范围的元素并添加到容器中
        for (let i = startIndex; i < endIndex && i < chatMessages.length; i++) {
            const message = chatMessages[i];
            if (i == startIndex) { // 判断一下在页面顶部多加一个时间
                if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(message.text)) {
                    // 时间戳转成时间
                    function timestampToTime(timestamp) {
                        let date = new Date(timestamp * 1000);
                        let year = date.getFullYear() + '-';
                        let month = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
                        let day = (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' ';
                        let hour = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
                        let minute = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':';
                        let second = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds();
                        return year + month + day + hour + minute + second;
                    }

                    // 添加div
                    const newTimeMessage = document.createElement('div');
                    newTimeMessage.className = "item item-center";
                    newTimeMessage.innerHTML = `<span>${timestampToTime(message.timestamp)}</span>`;
                    chatContainer.appendChild(newTimeMessage);
                    console.log("增加时间元素", timestampToTime(message.timestamp));
                }
            }
            const messageElement = document.createElement('div'); // 下面那俩的合体
            const avatarTag = avatarBox(message); // 头像
            const messageContent = document.createElement('div'); // 除了avatar之外的所有
            const side = message.is_send ? "right" : "left";
            if (message.type == 1) {
                // displayname 和 bubble
                messageContent.className = `content-wrapper content-wrapper-${side}`;
                if (message.is_chatroom && !message.is_send) {
                    messageContent.appendChild(displayNameBox(message));
                }
                messageContent.appendChild(messageBubble(message, side));

                // 整合
                messageElement.className = `item item-${side}`;
                messageElement.appendChild(message.is_send ? messageContent : avatarTag);
                messageElement.appendChild(message.is_send ? avatarTag : messageContent);
            }
            else if (message.type == 0) {
                messageElement.className = "item item-center";
                messageElement.innerHTML = `<span>${message.text}</span>`;
            }
            else if (message.type == 3) {
                // displayname 和 img
                messageContent.className = `content-wrapper content-wrapper-${side}`;
                if (message.is_chatroom && !message.is_send) {
                    messageContent.appendChild(displayNameBox(message));
                }
                messageContent.appendChild(messageImgBox(message));

                // 整合
                messageElement.className = `item item-${side}`;
                messageElement.appendChild(message.is_send ? messageContent : avatarTag);
                messageElement.appendChild(message.is_send ? avatarTag : messageContent);
            }
            else if (message.type == 43) {
                // displayname 和 video
                messageContent.className = `content-wrapper content-wrapper-${side}`;
                if (message.is_chatroom && !message.is_send) {
                    messageContent.appendChild(displayNameBox(message));
                }
                messageContent.appendChild(messageVideoBox(message));

                // 整合
                messageElement.className = `item item-${side}`;
                messageElement.appendChild(message.is_send ? messageContent : avatarTag);
                messageElement.appendChild(message.is_send ? avatarTag : messageContent);
            }
            else if (message.type == 49) {
                if (message.sub_type == 57) {
                    // displayname 和 bubble 和 refer
                    messageContent.className = `content-wrapper content-wrapper-${side}`;
                    if (message.is_chatroom && !message.is_send) {
                        messageContent.appendChild(displayNameBox(message));
                    }
                    messageContent.appendChild(messageBubble(message, side));
                    if (message.refer_text) {
                        messageContent.appendChild(messageElementReferText(message, side));
                    }

                    // 整合
                    messageElement.className = `item item-${side}`;
                    messageElement.appendChild(message.is_send ? messageContent : avatarTag);
                    messageElement.appendChild(message.is_send ? avatarTag : messageContent);
                }
            }
            else if (message.type == 34) {
                // displayname 和 转的文字 和 audio
                messageContent.className = `content-wrapper content-wrapper-${side}`;
                if (message.is_chatroom && !message.is_send) {
                    messageContent.appendChild(displayNameBox(message));
                }
                if (message.voice_to_text) {
                    messageContent.appendChild(messageVoiceToTextBubble(message, side));
                }
                messageContent.appendChild(messageAudioBox(message));

                // 整合
                messageElement.className = `item item-${side}`;
                messageElement.appendChild(message.is_send ? messageContent : avatarTag);
                messageElement.appendChild(message.is_send ? avatarTag : messageContent);
            }
            chatContainer.appendChild(messageElement);
        }
        document.querySelector("#chat-container").scrollTop = 0;
        updatePaginationInfo();
        refreshMediaListener();
    }

    function prevPage() {
        if (currentPage > 1) {
            currentPage--;
            renderPage(currentPage);
        }
    }

    function nextPage() {
        const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderPage(currentPage);
        }
    }
    function updatePaginationInfo() {
        const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
        const paginationInfo = document.getElementById('paginationInfo');
        paginationInfo.textContent = `共 ${totalPages} 页，当前第 ${currentPage} 页`;
    }
    function gotoPage() {
        const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
        const inputElement = document.getElementById('gotoPageInput');
        const targetPage = parseInt(inputElement.value);

        if (targetPage >= 1 && targetPage <= totalPages) {
            currentPage = targetPage;
            renderPage(currentPage);
        } else {
            alert('请输入有效的页码');
        }
    }

    // 初始化页面
    renderPage(currentPage);

    function refreshMediaListener() {
        const audioTags = document.querySelectorAll('audio');
        const videoTags = document.querySelectorAll('video');
        
        audioTags.forEach(audio => {
            audio.addEventListener('play', function () {
                pauseOtherMedia(audio);
            });
        });
        videoTags.forEach(video => {
            video.addEventListener('play', function () {
                pauseOtherMedia(video);
            });
        });

        function pauseOtherMedia(currentMedia) {
            const audioTags = document.querySelectorAll('audio');
            const videoTags = document.querySelectorAll('video');
            audioTags.forEach(media => {
                if (media !== currentMedia && !media.paused) {
                    media.pause();
                }
            });
            videoTags.forEach(media => {
                if (media !== currentMedia && !media.paused) {
                    media.pause();
                }
            });
        }
    }

    refreshMediaListener();
</script>

<script>
    function showModal(image) {
        var modal = document.getElementById("modal");
        var modalImage = document.getElementById("modal-image");
        modal.style.display = "block";
        modalImage.src = image.src;
        console.log(image.src);
    }

    function hideModal() {
        var modal = document.getElementById("modal");
        modal.style.display = "none";
    }
</script>
</body>
</html>
'''
