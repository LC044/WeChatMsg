import os

import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread

from . import msg
from ..log import log
from ..person import MePC

if not os.path.exists('./data/聊天记录'):
    os.mkdir('./data/聊天记录')


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

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.last_timestamp = 0
        self.sec = 2  # 默认1000秒
        self.contact = contact
        self.ta_username = contact.wxid
        self.msg_id = 0
        self.output_type = type_
        self.total_num = 0
        self.num = 0

    @log
    def to_csv(self, conRemark, path):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        if not os.path.exists(origin_docx_path):
            os.mkdir(origin_docx_path)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg.get_messages(self.contact.wxid)
        # print()
        df = pd.DataFrame(
            data=messages,
            columns=columns,
        )
        df.to_csv(filename, encoding='utf-8')
        self.okSignal.emit('ok')

    def to_html(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        if not os.path.exists(origin_docx_path):
            os.mkdir(origin_docx_path)
        messages = msg.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        f = open(filename, 'w', encoding='utf-8')
        html_head = '''
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
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
    .container{
        height: 760px;
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
    .item{
        margin-top: 15px;
        display: flex;
        width: 100%;
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

    .avatar img{
        width: 42px;
        height: 42px;
        border-radius: 50%;
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
    </style>
</head>
<body>
<div class="container">
    <div class="content">
        '''
        f.write(html_head)
        MePC().avatar.save(os.path.join(origin_docx_path, 'myhead.png'))
        self.contact.avatar.save(os.path.join(origin_docx_path, 'tahead.png'))
        for message in messages:
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            avatar = MePC().avatar_path if is_send else self.contact.avatar_path
            timestamp = message[5]
            if type_ == 1:
                if self.is_5_min(timestamp):
                    f.write(
                        f'''
                        <div class="item item-center"><span>{str_time}</span></div>
                        '''
                    )
                if is_send:
                    f.write(
                        f'''
                        <div class="item item-right">
            <div class="bubble bubble-right">{str_content}</div>
            <div class="avatar">
                <img src="myhead.png" />
            </div>
        </div>
                        '''
                    )
                else:
                    f.write(
                        f'''
                        <div class="item item-left">
            <div class="avatar">
                <img src="tahead.png" />
            </div>
            <div class="bubble bubble-left">{str_content}
            </div>
        </div>
                        '''
                    )
        html_end = '''
        
    </div>
</div>
</body>
</html>
        '''
        f.write(html_end)
        f.close()
        self.okSignal.emit('ok')

    def is_5_min(self, timestamp):
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp

            return True
        return False

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV:
            # print("线程导出csv")
            self.to_csv(self.ta_username, "path")
        elif self.output_type == self.HTML:
            self.to_html()
