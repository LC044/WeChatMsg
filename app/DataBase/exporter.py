import csv
import html
import os
import shutil
import sys

import filecmp

from PyQt5.QtCore import pyqtSignal, QThread

from ..config import output_dir
from ..person import Me, Contact

os.makedirs(os.path.join(output_dir, '聊天记录'), exist_ok=True)


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
    resource_dir = os.path.join('app', 'resources', 'data', 'icons')
    if not os.path.exists(resource_dir):
        # 获取打包后的资源目录
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        # 构建 FFmpeg 可执行文件的路径
        resource_dir = os.path.join(resource_dir, 'app', 'resources', 'data', 'icons')
    target_folder = os.path.join(path, 'icon')
    # 拷贝一些必备的图标
    for root, dirs, files in os.walk(resource_dir):
        relative_path = os.path.relpath(root, resource_dir)
        target_path = os.path.join(target_folder, relative_path)

        # 遍历文件夹中的文件
        for file in files:
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, file)
            if not os.path.exists(target_file_path):
                shutil.copy(source_file_path, target_file_path)
            else:
                # 比较文件内容
                if not filecmp.cmp(source_file_path, target_file_path, shallow=False):
                    # 文件内容不一致，进行覆盖拷贝
                    shutil.copy(source_file_path, target_file_path)


def escape_js_and_html(input_str):
    if not input_str:
        return ''
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

    def __init__(self, contact, type_=DOCX, message_types={}, time_range=None, messages=None,index=0, parent=None):
        super().__init__(parent)
        self.message_types = message_types  # 导出的消息类型
        self.contact: Contact = contact  # 联系人
        self.output_type = type_  # 导出文件类型
        self.total_num = 1  # 总的消息数量
        self.num = 0  # 当前处理的消息数量
        self.index = index #
        self.last_timestamp = 0
        self.time_range = time_range
        self.messages = messages
        origin_path = os.path.join(os.path.abspath('.'),output_dir,'聊天记录',self.contact.remark)
        makedirs(origin_path)

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
        if is_absolute_path:
            if self.contact.is_chatroom:
                avatar = message[13].avatar_path
            else:
                avatar = Me().avatar_path if is_send else self.contact.avatar_path
        else:
            if self.contact.is_chatroom:
                avatar = message[13].smallHeadImgUrl
            else:
                avatar = Me().smallHeadImgUrl if is_send else self.contact.smallHeadImgUrl
        return avatar

    def get_display_name(self, is_send, message) -> str:
        if self.contact.is_chatroom:
            if is_send:
                display_name = Me().name
            else:
                display_name = message[13].remark
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
