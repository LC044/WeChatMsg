import os

from app.DataBase import msg_db
from app.DataBase.exporter import ExporterBase
from app.config import output_dir
from app.util.compress_content import parser_reply, share_card


class TxtExporter(ExporterBase):
    def text(self, doc, message):
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        name = display_name
        doc.write(
            f'''{str_time} {name}\n{str_content}\n\n'''
        )

    def image(self, doc, message):
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[图片]\n\n'''
        )

    def audio(self, doc, message):
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[语音]\n\n'''
        )
    def emoji(self, doc, message):
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[表情包]\n\n'''
        )

    def file(self, doc, message):
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[文件]\n\n'''
        )

    def refermsg(self, doc, message):
        """
        处理回复消息
        @param doc:
        @param message:
        @return:
        """
        str_time = message[8]
        is_send = message[4]
        content = parser_reply(message[11])
        refer_msg = content.get('refer')
        display_name = self.get_display_name(is_send, message)
        if refer_msg:
            doc.write(
                f'''{str_time} {display_name}\n{content.get('title')}\n引用:{refer_msg.get('displayname')}:{refer_msg.get('content')}\n\n'''
            )
        else:
            doc.write(
                f'''{str_time} {display_name}\n{content.get('title')}\n引用:未知\n\n'''
            )

    def system_msg(self, doc, message):
        str_content = message[7]
        str_time = message[8]
        str_content = str_content.replace('<![CDATA[', "").replace(
            ' <a href="weixin://revoke_edit_click">重新编辑</a>]]>', "")
        doc.write(
            f'''{str_time} {str_content}\n\n'''
        )

    def video(self, doc, message):
        str_time = message[8]
        is_send = message[4]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[视频]\n\n'''
        )
    def music_share(self, doc, message):
        is_send = message[4]
        str_time = message[8]
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}\n[音乐分享]\n\n'''
        )

    def share_card(self, doc, message):
        is_send = message[4]
        bytesExtra = message[10]
        compress_content_ = message[11]
        str_time = message[8]
        card_data = share_card(bytesExtra, compress_content_)
        display_name = self.get_display_name(is_send, message)
        doc.write(
            f'''{str_time} {display_name}
            [链接]:title:{card_data.get('title')}
            description:{card_data.get('description')}
            url:{card_data.get('url')}
            name:{card_data.get('app_name')}
            \n\n'''
        )

    def export(self):
        # 实现导出为txt的逻辑
        print(f"【开始导出 TXT {self.contact.remark}】")
        origin_path = os.path.join(os.path.abspath('.'), output_dir, '聊天记录', self.contact.remark)
        os.makedirs(origin_path, exist_ok=True)
        filename = os.path.join(origin_path, self.contact.remark+'.txt')
        messages = msg_db.get_messages(self.contact.wxid, time_range=self.time_range)
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
                elif type_ == 49 and sub_type == 57 and self.message_types.get(1):
                    self.refermsg(f, message)
                elif type_ == 49 and sub_type == 6 and self.message_types.get(4906):
                    self.file(f, message)
                elif type_ == 49 and sub_type == 3 and self.message_types.get(4903):
                    self.music_share(f, message)
                elif type_ == 49 and sub_type == 5 and self.message_types.get(4905):
                    self.share_card(f, message)
        print(f"【完成导出 TXT {self.contact.remark}】")
        self.okSignal.emit(1)