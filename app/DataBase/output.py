import os
import re
import time
import docx
import xmltodict
from docx import shared
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_COLOR_INDEX, WD_PARAGRAPH_ALIGNMENT
from docxcompose.composer import Composer
from PyQt5.QtCore import *
from . import data


def IS_5_min(last_m, now_m):
    '''
    #! 判断两次聊天时间是不是大于五分钟
    #! 若大于五分钟则显示时间
    #! 否则不显示
    '''
    '''两次聊天记录时间差，单位是秒'''
    dt = now_m - last_m
    return abs(dt // 1000) >= 300


def time_format(timestamp):
    '''
    #! 将字符串类型的时间戳转换成日期
    #! 返回格式化的时间字符串
    #! %Y-%m-%d %H:%M:%S
    '''
    timestamp = timestamp / 1000
    time_tuple = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)


class Output(QThread):
    """
    发送信息线程
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1

    def __init__(self, Me, ta_u, parent=None):
        super().__init__(parent)
        self.Me = Me
        self.sec = 2  # 默认1000秒
        self.ta_username = ta_u
        self.my_avatar = self.Me.my_avatar
        self.ta_avatar = data.get_avator(ta_u)
        self.msg_id = 0

    def merge_docx(self, conRemark, n):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{conRemark}"
        all_word = os.listdir(origin_docx_path)
        all_file_path = []
        for i in range(n):
            file_name = f"{conRemark}{i}.docx"
            all_file_path.append(origin_docx_path + '/' + file_name)
        filename = f"{conRemark}.docx"
        # print(all_file_path)
        doc = docx.Document()
        doc.save(origin_docx_path + '/' + filename)
        master = docx.Document(origin_docx_path + '/' + filename)
        middle_new_docx = Composer(master)
        num = 0
        for word in all_file_path:
            word_document = docx.Document(word)
            word_document.add_page_break()
            if num != 0:
                middle_new_docx.append(word_document)
            num = num + 1
        middle_new_docx.save(origin_docx_path + '/' + filename)

    def progress(self, value):
        self.i += 1
        # 处理完成之后将多个文件合并
        if self.i == self.total_num:
            QThread.sleep(1)
            conRemark = data.get_conRemark(self.ta_username)
            self.progressSignal.emit(self.total_num-1)
            self.merge_docx(conRemark, self.n)
            print('ok')
            self.progressSignal.emit(self.total_num)
            self.okSignal.emit(1)
        self.progressSignal.emit(self.i)

    def run(self):
        self.Child = {}
        if 1:
            conRemark = data.get_conRemark(self.ta_username)
            data.mkdir(f"{os.path.abspath('.')}/data/聊天记录/{conRemark}")
            messages = data.get_all_message(self.ta_username)
            self.total_num = len(messages)
            self.rangeSignal.emit(self.total_num)
            l = len(messages)
            self.n = 10
            for i in range(self.n):
                q = i * (l // self.n)
                p = (i + 1) * (l // self.n)
                if i == self.n - 1:
                    p = l
                len_data = messages[q:p]
                # self.to_docx(len_data, i, conRemark)
                self.Child[i] = ChildThread(self.Me, self.ta_username, len_data, conRemark,i)
                self.Child[i].progressSignal.connect(self.progress)
                self.Child[i].start()


class ChildThread(QThread):
    """
        子线程，用于导出部分聊天记录
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    i = 1

    def __init__(self, Me, ta_u, message, conRemark,num, parent=None):
        super().__init__(parent)
        self.Me = Me
        self.sec = 2  # 默认1000秒
        self.ta_username = ta_u
        self.num = num
        self.my_avatar = self.Me.my_avatar
        self.ta_avatar = data.get_avator(ta_u)
        self.conRemark = conRemark
        self.message = message
        self.msg_id = 0

    def create_table(self, doc, isSend):
        '''
        #! 创建一个1*2表格
        #! isSend = 1 (0,0)存聊天内容，(0,1)存头像
        #! isSend = 0 (0,0)存头像，(0,1)存聊天内容
        #! 返回聊天内容的坐标
        '''
        table = doc.add_table(rows=1, cols=2, style='Normal Table')
        table.cell(0, 1).height = shared.Inches(0.5)
        table.cell(0, 0).height = shared.Inches(0.5)
        text_size = 1
        if isSend:
            '''表格右对齐'''
            table.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            avatar = table.cell(0, 1).paragraphs[0].add_run()
            '''插入头像，设置头像宽度'''
            avatar.add_picture(self.my_avatar, width=shared.Inches(0.5))
            '''设置单元格宽度跟头像一致'''
            table.cell(0, 1).width = shared.Inches(0.5)
            content_cell = table.cell(0, 0)
            '''聊天内容右对齐'''
            content_cell.paragraphs[0].paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        else:
            avatar = table.cell(0, 0).paragraphs[0].add_run()
            avatar.add_picture(self.ta_avatar, width=shared.Inches(0.5))
            '''设置单元格宽度'''
            table.cell(0, 0).width = shared.Inches(0.5)
            content_cell = table.cell(0, 1)
        '''聊天内容垂直居中对齐'''
        content_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        return content_cell

    def text(self, doc, isSend, message, status):
        if status == 5:
            message += '（未发出） '
        content_cell = self.create_table(doc, isSend)
        content_cell.paragraphs[0].add_run(message)
        content_cell.paragraphs[0].font_size = shared.Inches(0.5)
        # self.self_text.emit(message)
        if isSend:
            p = content_cell.paragraphs[0]
            p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        doc.add_paragraph()

    def image(self, doc, isSend, Type, content, imgPath):
        '''
        #! 插入聊天图片
        #! isSend = 1 只有缩略图
        #! isSend = 0 有原图
        :param doc:
        :param isSend:
        :param Type:
        :param content:
        :param imgPath:
        :return:
        '''
        content = self.create_table(doc, isSend)
        run = content.paragraphs[0].add_run()
        if Type == 3:
            imgPath = imgPath.split('th_')[1]
            imgPath = f'./app/data/image2/{imgPath[0:2]}/{imgPath[2:4]}/th_{imgPath}'
            imgPath = data.clearImagePath(imgPath)
        try:
            run.add_picture(f'{imgPath}', height=shared.Inches(2))
            doc.add_paragraph()
        except Exception:
            print("Error!image")

        # run.add_picture(f'{Path}/{imgPath}', height=shared.Inches(2))

    def emoji(self, doc, isSend, content, imgPath):
        '''
        #! 添加表情包
        :param isSend:
        :param content:
        :param imgPath:
        :return:
        '''
        imgPath = data.get_emoji(imgPath)
        if 1:
            is_Exist = os.path.exists(imgPath)
            self.image(doc, isSend, Type=47, content=content, imgPath=imgPath)

    def wx_file(self, doc, isSend, content, status):
        '''
        #! 添加微信文件
        :param isSend:
        :param content:
        :param status:
        :return:
        '''
        pattern = re.compile(r"<title>(.*?)<")
        r = pattern.search(content).group()
        filename = r.lstrip('<title>').rstrip('<')
        self.text(doc, isSend, filename, status)

    def retract_message(self, doc, isSend, content, status):
        '''
        #! 显示撤回消息
        :param isSend:
        :param content:
        :param status:
        :return:
        '''
        paragraph = doc.add_paragraph(content)
        paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def reply(self, doc, isSend, content, status):
        '''
        #! 添加回复信息
        :param isSend:
        :param content:
        :param status:
        :return:
        '''
        pattern1 = re.compile(r"<title>(?P<title>(.*?))</title>")
        title = pattern1.search(content).groupdict()['title']
        pattern2 = re.compile(r"<displayname>(?P<displayname>(.*?))</displayname>")
        displayname = pattern2.search(content).groupdict()['displayname']
        '''匹配回复的回复'''
        pattern3 = re.compile(r"\n?title&gt;(?P<content>(.*?))\n?&lt;/title&gt")
        if not pattern3.search(content):
            if isSend == 0:
                '''匹配对方的回复'''
                pattern3 = re.compile(r"<content>(?P<content>(.*?))</content>")
            else:
                '''匹配自己的回复'''
                pattern3 = re.compile(r"</msgsource>\n?<content>(?P<content>(.*?))\n?</content>")

        '''这部分代码完全可以用if代替'''

        try:
            '''试错'''
            text = pattern3.search(content).groupdict()['content']
        except Exception:
            try:
                '''试错'''
                text = pattern3.search(content).groupdict()['content']
            except Exception:
                '''试错'''
                pattern3 = re.compile(r"\n?<content>(?P<content>(.*?))\n?</content>")
                '''试错'''
                if pattern3.search(content):
                    text = pattern3.search(content).groupdict()['content']
                else:
                    text = '图片'
        if status == 5:
            message = '（未发出） ' + ''
        content_cell = self.create_table(doc, isSend)
        content_cell.paragraphs[0].add_run(title)
        content_cell.paragraphs[0].font_size = shared.Inches(0.5)
        reply_p = content_cell.add_paragraph()
        run = content_cell.paragraphs[1].add_run(displayname + ':' + text)
        '''设置被回复内容格式'''
        run.font.color.rgb = shared.RGBColor(121, 121, 121)
        run.font_size = shared.Inches(0.3)
        run.font.highlight_color = WD_COLOR_INDEX.GRAY_25

        if isSend:
            p = content_cell.paragraphs[0]
            p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            reply_p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        doc.add_paragraph()

    def pat_a_pat(self, doc, isSend, content, status):
        '''
        #! 添加拍一拍信息
        todo 把wxid转化成昵称
        :param isSend:
        :param content:
        :param status:
        :return:
        '''
        pat_data = xmltodict.parse(content)
        pat_data = pat_data['msg']['appmsg']['patMsg']['records']['record']
        fromUser = pat_data['fromUser']
        pattedUser = pat_data['pattedUser']
        template = pat_data['template']
        template = ''.join(template.split('${pattedusername@textstatusicon}'))
        template = ''.join(template.split('${fromusername@textstatusicon}'))
        template = template.replace(f'${{{fromUser}}}', data.get_conRemark(fromUser))
        template = template.replace(f'${{{pattedUser}}}', data.get_conRemark(pattedUser))
        print(template)
        p = doc.add_paragraph()
        run = p.add_run(template)
        p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        '''设置拍一拍文字格式'''
        run.font.color.rgb = shared.RGBColor(121, 121, 121)
        run.font_size = shared.Inches(0.3)
        # run.font.highlight_color=WD_COLOR_INDEX.GRAY_25

    def video(self, doc, isSend, content, status, img_path):
        print(content, img_path)

    def to_docx(self, messages, i, conRemark):
        '''创建联系人目录'''

        filename = f"{os.path.abspath('.')}/data/聊天记录/{conRemark}/{conRemark}{i}.docx"
        doc = docx.Document()
        last_timestamp = 1601968667000

        for message in messages:
            self.progressSignal.emit(self.i)
            self.i += 1
            msgId = message[0]
            ta_username = message[7]
            Type = int(message[2])
            isSend = message[4]
            content = message[8]
            imgPath = message[9]
            now_timestamp = message[6]
            status = message[3]
            createTime = time_format(now_timestamp)
            # print(createTime, isSend, content)
            if IS_5_min(last_timestamp, now_timestamp):
                doc.add_paragraph(createTime).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            last_timestamp = now_timestamp
            if Type == 1:
                try:
                    self.text(doc, isSend, content, status)
                except Exception as e:
                    print(e)
            elif Type == 3:
                self.image(doc, isSend, 3, content, imgPath)
            elif Type == 47:
                self.emoji(doc, isSend, content, imgPath)
            elif Type == 1090519089:
                self.wx_file(doc, isSend, content, status)
            elif Type == 268445456:
                self.retract_message(doc, isSend, content, status)
            elif Type == 822083633:
                self.reply(doc, isSend, content, status)
            elif Type == 922746929:
                self.pat_a_pat(doc, isSend, content, status)
            elif Type == 43:
                # print(createTime)
                self.video(doc, isSend, content, status, imgPath)
        # doc.add_paragraph(str(i))
        print(filename)
        doc.save(filename)

    def run(self):

        self.to_docx(self.message, self.num, self.conRemark)


if __name__ == '__main__':
    me = data.Me('wxid_27hqbq7vx5hf22')
    t = Output(Me=me, ta_u='wxid_q3ozn70pweud22')
    t.run()
