import csv
import html
import os

from PyQt5.QtCore import pyqtSignal, QThread

from . import msg_db
from ..DataBase import hard_link_db
from ..person_pc import MePC
from ..util import get_abs_path

os.makedirs('./data/聊天记录', exist_ok=True)


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

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.Child0 = None
        self.last_timestamp = 0
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
        filename = f"{os.path.abspath('.')}/data/聊天记录/messages.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg_db.get_messages_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV_ALL:
            self.to_csv_all()
        else:
            self.Child = ChildThread(self.contact, type_=self.output_type)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()

    def cancel(self):
        self.requestInterruption()


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

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.contact = contact
        self.last_timestamp = 0
        self.sec = 2  # 默认1000秒
        self.msg_id = 0
        self.output_type = type_

    def is_5_min(self, timestamp):
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp
            return True
        return False

    def text(self, doc, isSend, message, status):
        return

    def image(self, doc, isSend, Type, content, imgPath):
        return

    def emoji(self, doc, isSend, content, imgPath):
        return

    def wx_file(self, doc, isSend, content, status):
        return

    def retract_message(self, doc, isSend, content, status):
        return

    def reply(self, doc, isSend, content, status):
        return

    def pat_a_pat(self, doc, isSend, content, status):
        return

    def video(self, doc, isSend, content, status, img_path):
        return

    def to_csv(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.csv"
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
        self.okSignal.emit('ok')

    def to_csv_all(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/messages.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg_db.get_messages_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def to_html(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        messages = msg_db.get_messages(self.contact.wxid)
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
        <div class="container" id="container" onscroll="handleScroll()">
            <div class="content">
                '''
        f.write(html_head)
        MePC().avatar.save(os.path.join(origin_docx_path, 'myhead.png'))
        self.contact.avatar.save(os.path.join(origin_docx_path, 'tahead.png'))
        self.rangeSignal.emit(len(messages))
        for index, message in enumerate(messages):
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            avatar = MePC().avatar_path if is_send else self.contact.avatar_path
            timestamp = message[5]
            self.progressSignal.emit(index)
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
        <script>
  const container = document.getElementById('container');
  const content = document.getElementById('content');

  const totalItems = 1000;
  const itemsPerPage = 20;
  const itemHeight = 50;

  function updateContent() {
    const scrollTop = container.scrollTop;
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

    // Remove existing items
    content.innerHTML = '';

    // Add new items
    for (let i = startIndex; i < endIndex; i++) {
      const item = document.createElement('div');
      item.className = 'item';
      item.textContent = `Item ${i}`;
      content.appendChild(item);
    }

    // Update container height to show correct scrollbar
    container.style.height = totalItems * itemHeight + 'px';
  }

  function handleScroll() {
    updateContent();
  }

  // Initial content rendering
  updateContent();
</script>
        </body>
        </html>
                '''
        f.write(html_end)
        f.close()
        self.okSignal.emit(1)

    def to_html_(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        messages = msg_db.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        f = open(filename, 'w', encoding='utf-8')
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
      margin: auto;
      margin-top: 5%;
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
    <input type="number" id="gotoPageInput" placeholder="跳转到第几页">
    <button onclick="gotoPage()">跳转</button>
  </div>
  <div id="paginationInfo"></div>
</div>
<script>
const chatContainer = document.getElementById('chat-container');
// Sample chat messages (replace this with your actual data)
const chatMessages = [
        '''
        f.write(html_head)
        MePC().avatar.save(os.path.join(origin_docx_path, 'myhead.png'))
        self.contact.avatar.save(os.path.join(origin_docx_path, 'tahead.png'))
        self.rangeSignal.emit(len(messages))
        for index, message in enumerate(messages):
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            # avatar = MePC().avatar_path if is_send else self.contact.avatar_path
            # avatar = avatar.replace('\\', '\\\\')
            avatar = 'myhead.png' if is_send else 'tahead.png'
            timestamp = message[5]
            self.progressSignal.emit(index)
            if type_ == 1:
                str_content = escape_js_and_html(str_content)
                if self.is_5_min(timestamp):
                    f.write(
                        f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:''}},'''
                    )
                f.write(
                    f'''{{ type:{type_}, text: '{str_content}',is_send:{is_send},avatar_path:'{avatar}'}},'''
                )
            elif type_ == 3:
                import re
                pattern1 = r'<msg><img length="\d+" hdlength="0" /><commenturl></commenturl></msg>'
                pattern2 = r'<msg><img /></msg>'
                match = re.search(pattern1, str_content)
                if match:
                    continue
                match = re.search(pattern2, str_content)
                if match:
                    continue

                image_path = hard_link_db.get_image(content=str_content, thumb=False)
                image_path = get_abs_path(image_path)
                image_path = image_path.replace('\\', '/')
                # print(f"tohtml:---{image_path}")
                if self.is_5_min(timestamp):
                    f.write(
                        f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:''}},'''
                    )
                f.write(
                    f'''{{ type:{type_}, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}'}},'''
                )
        html_end = '''
];
    function renderMessages(messages) {
        for (const message of messages) {
            const messageElement = document.createElement('div');
            if (message.type == 1){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='bubble bubble-right'>${message.text}</div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='bubble bubble-right'>${message.text}</div>`
            }
            }
            else if(message.type == 0){
                messageElement.className = "item item-center";
                messageElement.innerHTML = `<span>${message.text}</span>`
            }
            else if (message.type == 3){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='chat-image'><img src="${message.text}" /></div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='chat-image'><img src="${message.text}" /></div>`
            }
            }
            chatContainer.appendChild(messageElement);
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
    // 从数据列表中取出对应范围的元素并添加到容器中
    for (let i = startIndex; i < endIndex && i < chatMessages.length; i++) {
        const message = chatMessages[i];
        const messageElement = document.createElement('div');
            if (message.type == 1){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='bubble bubble-right'>${message.text}</div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='bubble bubble-right'>${message.text}</div>`
            }
            }
            else if(message.type == 0){
                messageElement.className = "item item-center";
                messageElement.innerHTML = `<span>${message.text}</span>`
            }
            else if (message.type == 3){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='chat-image' ><img src="${message.text}" onclick="showModal(this)"/></div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}"/></div><div class='chat-image'><img src="${message.text}" onclick="showModal(this)"/></div>`
            }
            }
            chatContainer.appendChild(messageElement);
    }
    updatePaginationInfo();
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
        f.write(html_end)
        f.close()
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

    def cancel(self):
        self.requestInterruption()
