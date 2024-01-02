import csv
import html
import os
import shutil
import sys
import time
import traceback
from re import findall

import docx
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog
from docx import shared
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_COLOR_INDEX, WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn

from .package_msg import PackageMsg
from ..DataBase import media_msg_db, hard_link_db, micro_msg_db, msg_db
from ..log import logger
from ..person import Me, Contact
from ..util import path
from ..util.compress_content import parser_reply, music_share, share_card
from ..util.emoji import get_emoji_url
from ..util.file import get_file
from ..util.music import get_music_path
from ..util.image import get_image_path, get_image, get_image_abs_path

os.makedirs('./data/聊天记录', exist_ok=True)


def set_global_font(doc, font_name):
    # 创建一个新样式
    style = doc.styles['Normal']

    # 设置字体名称
    style.font.name = font_name
    # 遍历文档中的所有段落，将样式应用到每个段落
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name


def makedirs(path):
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, 'image'), exist_ok=True)
    os.makedirs(os.path.join(path, 'emoji'), exist_ok=True)
    os.makedirs(os.path.join(path, 'video'), exist_ok=True)
    os.makedirs(os.path.join(path, 'voice'), exist_ok=True)
    os.makedirs(os.path.join(path, 'file'), exist_ok=True)
    os.makedirs(os.path.join(path, 'avatar'), exist_ok=True)
    os.makedirs(os.path.join(path, 'music'), exist_ok=True)
    os.makedirs(os.path.join(path, 'icon'), exist_ok=True)
    file = './app/resources/data/file.png'
    if not os.path.exists(file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        file = os.path.join(resource_dir, 'app', 'resources', 'data', 'file.png')
    shutil.copy(file, path + '/icon/file.png')
    play_file = './app/resources/data/play.png'
    if not os.path.exists(play_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        play_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'play.png')
    shutil.copy(play_file, path + '/icon/play.png')
    pause_file = './app/resources/data/pause.png'
    if not os.path.exists(pause_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        pause_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'pause.png')
    shutil.copy(pause_file, path + '/icon/pause.png')


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


class ExporterBase(QThread):
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
        self.message_types = message_types  # 导出的消息类型
        self.contact: Contact = contact  # 联系人
        self.output_type = type_  # 导出文件类型
        self.total_num = 1  # 总的消息数量
        self.num = 0  # 当前处理的消息数量
        self.last_timestamp = 0
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        makedirs(origin_docx_path)
    def run(self):
        self.export()
    def export(self):
        raise NotImplementedError("export method must be implemented in subclasses")

    def cancel(self):
        self.requestInterruption()

    def is_5_min(self, timestamp) -> bool:
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp
            return True
        return False

    def get_avatar_path(self, is_send, message, is_absolute_path=False) -> str:
        if self.contact.is_chatroom:
            avatar = message[12].smallHeadImgUrl
        else:
            avatar = Me().smallHeadImgUrl if is_send else self.contact.smallHeadImgUrl
        if is_absolute_path:
            if self.contact.is_chatroom:
                avatar = message[12].avatar_path
            else:
                avatar = Me().avatar_path if is_send else self.contact.avatar_path
        return avatar

    def get_display_name(self, is_send, message) -> str:
        if self.contact.is_chatroom:
            if is_send:
                display_name = Me().name
            else:
                display_name = message[12].remark
        else:
            display_name = Me().name if is_send else self.contact.remark
        return escape_js_and_html(display_name)

    def text(self, doc, message):
        return

    def image(self, doc, message):
        return

    def audio(self, doc, message):
        return

    def emoji(self, doc, message):
        return

    def file(self, doc, message):
        return

    def refermsg(self, doc, message):
        return

    def system_msg(self, doc, message):
        return

    def video(self, doc, message):
        return

    def music_share(self, doc, message):
        return

    def share_card(self, doc, message):
        return