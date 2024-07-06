import os
import re

from app.DataBase import msg_db
from app.util.compress_content import parser_reply, share_card
from app.util.exporter.exporter import ExporterBase


def remove_privacy_info(text):
    # 正则表达式模式
    patterns = {
        'phone': r'\b(\+?86[-\s]?)?1[3-9]\d{9}\b',  # 手机号
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        'id_card': r'\b\d{15}|\d{18}|\d{17}X\b',  # 身份证号
        'password': r'\b(?:password|pwd|pass|psw)[\s=:]*\S+\b',  # 密码
        'account': r'\b(?:account|username|user|acct)[\s=:]*\S+\b'  # 账号
    }

    for key, pattern in patterns.items():
        text = re.sub(pattern, f'[{key} xxx]', text)

    return text


class AiTxtExporter(ExporterBase):
    last_is_send = -1

    def title(self, message):
        str_time = message[8]
        is_send = message[4]
        display_name = ''
        if is_send != self.last_is_send:
            display_name = '\n' + self.get_display_name(is_send, message) + ':'
        self.last_is_send = is_send
        return display_name

    def text(self, doc, message):
        str_content = remove_privacy_info(message[7])
        doc.write(
            f'''{self.title(message)}{str_content} '''
        )

    def image(self, doc, message):
        doc.write(
            f'''{self.title(message)}[图片]'''
        )

    def audio(self, doc, message):
        doc.write(
            f'''{self.title(message)}[语音]'''
        )

    def emoji(self, doc, message):
        doc.write(
            f'''{self.title(message)}[表情包]'''
        )

    def file(self, doc, message):
        doc.write(
            f'''{self.title(message)}[文件]'''
        )

    def system_msg(self, doc, message):
        str_content = message[7]
        str_time = message[8]
        str_content = str_content.replace('<![CDATA[', "").replace(
            ' <a href="weixin://revoke_edit_click">重新编辑</a>]]>', "")
        doc.write(
            f'''{str_time} {str_content}'''
        )

    def video(self, doc, message):
        is_send = message[4]
        doc.write(
            f'''{self.title(message)}[视频]'''
        )

    def export(self):
        # 实现导出为txt的逻辑
        print(f"【开始导出 TXT {self.contact.remark}】")
        origin_path = self.origin_path
        os.makedirs(origin_path, exist_ok=True)
        filename = os.path.join(origin_path, self.contact.remark + '_chat.txt')
        messages = msg_db.get_messages_group_by_day(self.contact.wxid, time_range=self.time_range)
        total_steps = len(messages)
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            for date, messages in messages.items():
                f.write(f"\n\n{'*' * 20}{date}{'*' * 20}\n")
                for index, message in enumerate(messages):
                    type_ = message[2]
                    sub_type = message[3]
                    self.progressSignal.emit(int((index + 1) / total_steps * 100))
                    if type_ == 1 and self.message_types.get(type_):
                        self.text(f, message)
        print(f"【完成导出 TXT {self.contact.remark}】")
        self.okSignal.emit(1)
