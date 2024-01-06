import os
import shutil
import sys
import traceback
from re import findall

from PyQt5.QtCore import pyqtSignal, QThread

from app.DataBase import msg_db, hard_link_db, media_msg_db
from app.DataBase.output import ExporterBase, escape_js_and_html
from app.DataBase.package_msg import PackageMsg
from app.log import logger
from app.person import Me
from app.util import path
from app.util.compress_content import parser_reply, share_card, music_share, file
from app.util.emoji import get_emoji_url
from app.util.image import get_image_path, get_image
from app.util.music import get_music_path
from app.util.file import escape_single_quotes


icon_files = {
    './icon/word.png': ['doc', 'docx'],
    './icon/excel.png': ['xls', 'xlsx'],
    './icon/csv.png': ['csv'],
    './icon/txt.png': ['txt'],
    './icon/zip.png': ['zip', '7z','rar'],
    './icon/ppt.png': ['ppt', 'pptx'],
    './icon/pdf.png': ['pdf'],
}



class HtmlExporter(ExporterBase):
    def text(self, doc, message):
        type_ = message[2]
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0

        display_name = self.get_display_name(is_send, message)
        avatar = self.get_avatar_path(is_send, message)
        str_content = escape_js_and_html(str_content)
        doc.write(
            f'''{{ type:{1}, text: '{str_content}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
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
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        str_content = escape_js_and_html(str_content)
        image_path = hard_link_db.get_image(str_content, BytesExtra, thumb=False)
        if not os.path.exists(os.path.join(Me().wx_dir, image_path)):
            image_thumb_path = hard_link_db.get_image(str_content, BytesExtra, thumb=True)
            if not os.path.exists(os.path.join(Me().wx_dir, image_thumb_path)):
                return
            image_path = image_thumb_path
        image_path = get_image_path(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
        doc.write(
            f'''{{ type:{type_}, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
        )

    def audio(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        msgSvrId = message[9]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        try:
            audio_path = media_msg_db.get_audio_path(msgSvrId, output_path=origin_docx_path + "/voice")
            audio_path = "./voice/" + os.path.basename(audio_path)
            voice_to_text = escape_js_and_html(media_msg_db.get_audio_text(str_content))
        except:
            logger.error(traceback.format_exc())
            return
        doc.write(
            f'''{{ type:34, text:'{audio_path}',is_send:{is_send},avatar_path:'{avatar}',voice_to_text:'{voice_to_text}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
        )

    def emoji(self, doc, message):
        str_content = message[7]
        str_time = message[8]
        is_send = message[4]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        emoji_path = get_emoji_url(str_content, thumb=True)
        doc.write(
            f'''{{ type:{3}, text: '{emoji_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
        )

    def file(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        bytesExtra = message[10]
        compress_content = message[11]
        str_time = message[8]
        is_send = message[4]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        file_info = file(bytesExtra, compress_content, output_path=origin_docx_path + '/file')
        if file_info.get('is_error') == False:
            icon_path = None
            for icon, extensions in icon_files.items():
                if file_info.get('file_ext') in extensions:
                    icon_path = icon
                    break
            # 如果没有与文件后缀匹配的图标，则使用默认图标
            if icon_path is None:
                default_icon = './icon/file.png'
                icon_path = default_icon
            file_path = file_info.get('file_path')
            if file_path != "":
                file_path = './file/' + file_info.get('file_name')
            file_path = escape_single_quotes(file_path)
            file_name = escape_single_quotes(file_info.get('file_name'))
            doc.write(
                f'''{{ type:49, text: '{file_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp}
                            ,is_chatroom:{is_chatroom},displayname:'{display_name}',icon_path: '{icon_path}'
                            ,sub_type:6,file_name: '{file_name}',file_size: '{file_info.get('file_len')}'
                            ,app_name: '{file_info.get('app_name')}'}},'''
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
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        contentText = escape_js_and_html(content.get('title'))
        if refer_msg:
            referText = f"{escape_js_and_html(refer_msg.get('displayname'))}：{escape_js_and_html(refer_msg.get('content'))}"
            doc.write(
                f'''{{ type:49, text: '{contentText}',is_send:{is_send},sub_type:{content.get('type')},refer_text: '{referText}',avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
            )
        else:
            doc.write(
                f'''{{ type:49, text: '{contentText}',is_send:{is_send},sub_type:{content.get('type')},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
            )

    def system_msg(self, doc, message):
        str_content = message[7]
        is_send = message[4]
        str_time = message[8]
        timestamp = message[5]
        is_chatroom = 1 if self.contact.is_chatroom else 0

        str_content = str_content.replace('<![CDATA[', "").replace(
            ' <a href="weixin://revoke_edit_click">重新编辑</a>]]>', "")
        res = findall('(</{0,1}(img|revo|_wc_cus|a).*?>)', str_content)
        for xmlstr, b in res:
            str_content = str_content.replace(xmlstr, "")
        str_content = escape_js_and_html(str_content)
        doc.write(
            f'''{{ type:0, text: '{str_content}',is_send:{is_send},avatar_path:'',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:''}},'''
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
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        video_path = hard_link_db.get_video(str_content, BytesExtra, thumb=False)
        image_path = hard_link_db.get_video(str_content, BytesExtra, thumb=True)
        if video_path is None and image_path is not None:
            image_path = path.get_relative_path(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
            try:
                # todo 网络图片问题
                print(origin_docx_path + image_path[1:])
                os.utime(origin_docx_path + image_path[1:], (timestamp, timestamp))
                doc.write(
                    f'''{{ type:3, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
                )
            except:
                doc.write(
                    f'''{{ type:1, text: '视频丢失',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
                )
            return
        if video_path is None and image_path is None:
            return
        video_path = f'{Me().wx_dir}/{video_path}'
        if os.path.exists(video_path):
            new_path = origin_docx_path + '/video/' + os.path.basename(video_path)
            if not os.path.exists(new_path):
                shutil.copy(video_path, os.path.join(origin_docx_path, 'video'))
            os.utime(new_path, (timestamp, timestamp))
            video_path = f'./video/{os.path.basename(video_path)}'
        doc.write(
            f'''{{ type:{type_}, text: '{video_path}',is_send:{is_send},avatar_path:'{avatar}',timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}'}},'''
        )

    def music_share(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        is_send = message[4]
        timestamp = message[5]
        content = music_share(message[11])
        music_path = ''
        if content.get('is_error') == False:
            if content.get('audio_url') != '':
                music_path = get_music_path(content.get('audio_url'), content.get('title'),
                                            output_path=origin_docx_path + '/music')
                if music_path != '':
                    music_path = f'./music/{os.path.basename(music_path)}'
                    music_path = music_path.replace('\\', '/')
            is_chatroom = 1 if self.contact.is_chatroom else 0
            avatar = self.get_avatar_path(is_send, message)
            display_name = self.get_display_name(is_send, message)
            doc.write(
                f'''{{ type:49, text:'{music_path}',is_send:{is_send},avatar_path:'{avatar}',link_url:'{content.get('link_url')}',
                timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}',sub_type:3,title:'{content.get('title')}',
                artist:'{content.get('artist')}', website_name:'{content.get('website_name')}'}},'''
            )

    def share_card(self, doc, message):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        is_send = message[4]
        timestamp = message[5]
        bytesExtra = message[10]
        compress_content_ = message[11]
        card_data = share_card(bytesExtra, compress_content_)
        is_chatroom = 1 if self.contact.is_chatroom else 0
        avatar = self.get_avatar_path(is_send, message)
        display_name = self.get_display_name(is_send, message)
        thumbnail = ''
        if card_data.get('thumbnail'):
            thumbnail = os.path.join(Me().wx_dir, card_data.get('thumbnail'))
            if os.path.exists(thumbnail):
                shutil.copy(thumbnail, os.path.join(origin_docx_path, 'image', os.path.basename(thumbnail)))
                thumbnail = './image/' + os.path.basename(thumbnail)
            else:
                thumbnail = ''
        app_logo = ''
        if card_data.get('app_logo'):
            app_logo = os.path.join(Me().wx_dir, card_data.get('app_logo'))
            if os.path.exists(app_logo):
                shutil.copy(app_logo, os.path.join(origin_docx_path, 'image', os.path.basename(app_logo)))
                app_logo = './image/' + os.path.basename(app_logo)
            else:
                app_logo = card_data.get('app_logo')
        doc.write(
            f'''{{ type:49,sub_type:5, text:'',is_send:{is_send},avatar_path:'{avatar}',url:'{card_data.get('url')}',
                    timestamp:{timestamp},is_chatroom:{is_chatroom},displayname:'{display_name}',title:'{card_data.get('title')}',
                    description:'{card_data.get('description')}',thumbnail:'{thumbnail}',app_logo:'{app_logo}',
                    app_name:'{card_data.get('app_name')}'
                    }},\n'''
        )

    def export(self):
        if self.contact.is_chatroom:
            packagemsg = PackageMsg()
            messages = packagemsg.get_package_message_by_wxid(self.contact.wxid)
        else:
            messages = msg_db.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        file_path = './app/resources/data/template.html'
        if not os.path.exists(file_path):
            resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            file_path = os.path.join(resource_dir, 'app', 'resources', 'data', 'template.html')

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            html_head, html_end = content.split('/*注意看这是分割线*/')
        f = open(filename, 'w', encoding='utf-8')
        f.write(html_head.replace("<title>Chat Records</title>", f"<title>{self.contact.remark}</title>"))
        self.rangeSignal.emit(len(messages))
        for index, message in enumerate(messages):
            type_ = message[2]
            sub_type = message[3]
            timestamp = message[5]
            if (type_ == 3 and self.message_types.get(3)) or (type_ == 34 and self.message_types.get(34)) or (
                    type_ == 47 and self.message_types.get(47)):
                pass
            else:
                self.progressSignal.emit(1)

            if self.is_5_min(timestamp):
                str_time = message[8]
                f.write(
                    f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:'',timestamp:{timestamp}}},'''
                )
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
        f.write(html_end)
        f.close()
        self.count_finish_num(1)

    def count_finish_num(self, num):
        """
        记录子线程完成个数
        @param num:
        @return:
        """
        self.num += 1
        print('子线程完成',self.num,'/',self.total_num)
        if self.num == self.total_num:
            # 所有子线程都完成之后就发送完成信号
            self.okSignal.emit(1)


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
        # sublist_length = len(messages) // self.child_thread_num
        # index = 0
        # for i in range(0, len(messages), sublist_length):
        #     child_messages = messages[i:i + sublist_length]
        #     self.child_threads[index] = OutputImageChild(self.contact, child_messages)
        #     self.child_threads[index].okSingal.connect(self.count1)
        #     self.child_threads[index].progressSignal.connect(self.progressSignal)
        #     self.child_threads[index].start()
        #     print('开启一个新线程')
        #     index += 1


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
