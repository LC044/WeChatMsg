# -*- coding: utf-8 -*-
"""
@File    : mainview.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : 主窗口
"""
import json
import os.path
import subprocess
import sys
import traceback
import requests
import time
from urllib.parse import urljoin

from PyQt5.QtCore import pyqtSignal, QThread, QSize, QUrl, Qt
from PyQt5.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox

from Custom_Widgets.Widgets import *

from app.DataBase import misc_db, micro_msg_db, close_db
from app.ui.Icon import Icon
from .interface import *
from app.ui.chat import ChatWindow
from app.ui.contact import ContactWindow
from app.ui.tool.tool_window import ToolWindow
from app.ui.home.home_window import HomeWindow, ReportThread
from app.ui.tool.setting.setting import ErrorThread
from app.ui.tool.pc_decrypt.pc_decrypt import DecryptThread, InfoThread
from app.ui.tool.get_bias_addr.get_bias_addr import BiasThread
from app.ui.chat.chat_info import ShowChatThread
from app.ui.chat.chat_window import ShowContactThread, ShowThread
from app.ui.menu.export import ShowContactExportThread, export_types, export_file_format
from app.util import path
from app.config import SERVER_API_URL
from app.decrypt.get_bias_addr import BiasAddr
from .menu.export import ExportDialog
from app.util.exporter.output import Output
from ..components.QCursorGif import QCursorGif
from ..config import INFO_FILE_PATH, DB_DIR, about, SERVER_API_URL, version
from ..log import logger
from ..person import Me

from app.DataBase import micro_msg_db, misc_db
from app.util.exporter.output import Output
from app.components import ScrollBar
from app.components.export_contact_item import ContactQListWidgetItem
from app.config import OUTPUT_DIR
from app.person import Contact
from app.ui.menu.exportUi import Ui_Dialog
from app.ui.menu.export_time_range import TimeRangeDialog

try:
    from app.ui.menu.about_dialog import version, UpdateThread, AboutDialog
except ModuleNotFoundError:
    logger.error(f'Python版本错误:Python>=3.10,仅支持3.10、3.11、3.12')
    raise ValueError('Python版本错误:Python>=3.10,仅支持3.10、3.11、3.12')


class Avatar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, e):
        super().mouseDoubleClickEvent()
        QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7"))

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7"))


class MainWinController(QMainWindow, Ui_MainWindow):
    exitSignal = pyqtSignal(bool)
    okSignal = pyqtSignal(bool)

    DecryptSignal = pyqtSignal(bool)
    get_wxidSignal = pyqtSignal(str)
    versionErrorSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWinController, self).__init__(parent)
        self.outputThread0 = None
        self.outputThread = None

        self.setupUi(self)

        self.load_flag = False
        self.load_data()
        self.load_num = 0

        loadJsonStyle(self, self, jsonFiles=["app/ui/style.json"])

        self.toolBtn.clicked.connect(lambda: self.centerMenuContainer.expandMenu())
        # self.msgBtn.clicked.connect(lambda: self.centerMenuContainer.expandMenu())
        # self.friendBtn.clicked.connect(lambda: self.centerMenuContainer.expandMenu())
        # self.userBtn.clicked.connect(lambda: self.centerMenuContainer.expandMenu())

        self.msgBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.friendBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.userBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.aboutBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.settingBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.helpBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())

        self.prepare_about()

        self.version_list = None
        self.versionText.setText(f"留痕-V{version}")

        self.closeCenterMenuBtn.clicked.connect(lambda: self.centerMenuContainer.collapseMenu())
        self.closeNotificationBtn.clicked.connect(lambda: self.popupNotificationsContainer.collapseMenu())

        self.exportAllBtn.clicked.connect(self.output)
        self.exportFriendBtn.clicked.connect(self.output)

        self.updateBtn.clicked.connect(self.update)

        self.questionBtn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7")))
        self.toolQuestionBtn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/4")))
        self.friendQuestionBtn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7")))
        self.msgQuestionBtn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7")))

        self.mainContentsPages.setCurrentWidget(self.aboutMainPage)

        self.reportBtn.clicked.connect(self.report)

        self.stopWordBtn.clicked.connect(self.add_stopwords)
        self.newWordBtn.clicked.connect(self.add_new_words)
        self.read_data()
        self.sendErrorBtn.clicked.connect(self.send_error_log)

        self.setBtnVisible(0)
        self.toolBtn.clicked.connect(lambda: self.setBtnVisible(1))
        self.decryptBtn.clicked.connect(lambda: self.setBtnVisible(1))
        self.decryptBtn2.clicked.connect(lambda: self.setBtnVisible(2))
        self.dataBtn.clicked.connect(lambda: self.setBtnVisible(3))
        self.msgBtn.clicked.connect(lambda: self.setBtnVisible(4))
        self.friendBtn.clicked.connect(lambda: self.setBtnVisible(5))
        self.userBtn.clicked.connect(lambda: self.setBtnVisible(6))
        self.aboutBtn.clicked.connect(lambda: self.setBtnVisible(7))
        self.settingBtn.clicked.connect(lambda: self.setBtnVisible(8))
        self.helpBtn.clicked.connect(lambda: self.setBtnVisible(9))

        self.startDecryptBtn.clicked.connect(self.decrypt)
        self.getInfoBtn.clicked.connect(self.get_info)
        self.dbDirBtn.clicked.connect(self.select_db_dir)
        self.lineEdit.returnPressed.connect(self.set_wxid)
        self.lineEdit.textChanged.connect(self.set_wxid_)

        self.startDecryptBiasBtn.clicked.connect(self.get_bias_addr)
        
        self.friendView = ContactWindow(parent=self.friendMainPage)
        self.msgView = ChatWindow(parent=self.msgMainPage)
        
        self.statisticBtn.clicked.connect(self.statistic)
        self.moodBtn.clicked.connect(self.mood)
        self.userReportBtn.clicked.connect(self.user_report)
        
        self.contacts = []
        self.btn_select_all.clicked.connect(self.select_all)
        self.select_all_flag = False
        self.exportBatchBtn.clicked.connect(self.export_data)
        self.comboBox_time.activated.connect(self.set_export_date)
        self.export_choices = {"文本": True, "图片": True, "语音": False, "视频": False, "表情包": False,
                               '音乐与音频': False, '分享卡片': False, '文件': False,
                               '转账': False, '音视频通话': False,'拍一拍等系统消息': True}
        self.checkBox_word.setEnabled(False)
        self.checkBox_word.setText('Docx(暂时不可用)')
        self.worker = None
        for export_type, default_state in self.export_choices.items():
            checkbox = QCheckBox(export_type)
            checkbox.setObjectName('message_type')
            checkbox.setChecked(default_state)
            self.messageTypeVerticalLayout.addWidget(checkbox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.messageTypeVerticalLayout.addItem(spacerItem1)
        self.timer = QTimer(self)
        self.time = 0
        self.total_msg_num = 99999
        self.num = 0
        self.timer.timeout.connect(self.update_elapsed_time)
        self.show_thread = ShowContactExportThread()
        self.show_thread.showSingal.connect(self.show_contact)
        self.show_thread.start()
        self.listWidget.setVerticalScrollBar(ScrollBar())
        self.listWidget.itemClicked.connect(self.setCurrentIndex)
        self.visited = set()
        self.now_index = 0
        self.time_range = None
        
    def setBtnVisible(self, index=0):
        self.getInfoBtn.setVisible(False)
        self.dbDirBtn.setVisible(False)
        self.startDecryptBtn.setVisible(False)
        self.startDecryptBiasBtn.setVisible(False)
        self.statisticBtn.setVisible(False)
        self.moodBtn.setVisible(False)
        self.reportBtn.setVisible(False)
        self.userReportBtn.setVisible(False)
        self.exportAllBtn.setVisible(False)
        self.exportBatchBtn.setVisible(False)
        self.exportFriendBtn.setVisible(False)
        self.stopWordBtn.setVisible(False)
        self.newWordBtn.setVisible(False)
        if index == 1:
            self.getInfoBtn.setVisible(True)
            self.dbDirBtn.setVisible(True)
            self.startDecryptBtn.setVisible(True)
        if index == 2:
            self.startDecryptBiasBtn.setVisible(True)
        if index == 3:
            self.exportAllBtn.setVisible(True)
            self.exportBatchBtn.setVisible(True)
            self.exportFriendBtn.setVisible(True)
        if index == 5:
            self.statisticBtn.setVisible(True)
            self.moodBtn.setVisible(True)
            self.userReportBtn.setVisible(True)
        if index == 6:
            self.reportBtn.setVisible(True)
        if index == 8:
            self.stopWordBtn.setVisible(True)
            self.newWordBtn.setVisible(True)

    def load_data(self):
        if os.path.exists(INFO_FILE_PATH):
            with open(INFO_FILE_PATH, 'r', encoding='utf-8') as f:
                dic = json.loads(f.read())
                wxid = dic.get('wxid')
                if wxid:
                    me = Me()
                    me.wxid = dic.get('wxid')
                    me.name = dic.get('name')
                    me.nickName = dic.get('name')
                    me.remark = dic.get('name')
                    me.mobile = dic.get('mobile')
                    me.wx_dir = dic.get('wx_dir')
                    me.token = dic.get('token')
                    self.set_my_info(wxid)
                    self.load_flag = True
        else:
            pass

    def set_my_info(self, wxid):
        self.avatar = QPixmap()
        img_bytes = misc_db.get_avatar_buffer(wxid)
        if not img_bytes:
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60)
        contact_info_list = micro_msg_db.get_contact_by_username(wxid)
        if not contact_info_list:
            close_db()
            import shutil
            try:
                shutil.rmtree(DB_DIR)
            except:
                pass
            self.message_error("数据库错误，请删除app文件夹后重启电脑再运行软件")
            return
        me = Me()
        me.set_avatar(img_bytes)
        me.smallHeadImgUrl = contact_info_list[7]
        self.myavatar.setScaledContents(True)
        self.myavatar.setPixmap(self.avatar)

    def output(self):
        if self.sender() == self.exportAllBtn:
            self.outputThread = Output(None, type_=Output.CSV_ALL)
            self.outputThread.okSignal.connect(
                lambda x: self.message_notification('聊天记录导出成功'))
            self.outputThread.start()
        elif self.sender() == self.exportFriendBtn:
            self.outputThread = Output(None, type_=Output.CONTACT_CSV)
            self.outputThread.okSignal.connect(
                lambda x: self.message_notification('联系人导出成功'))
            self.outputThread.start()
    
    def countLine(self, text):
        text = text.replace('<br>', '\n')
        lines = len(text.split('\n'))
        return lines - 1

    def message_notification(self, msg):
        self.notificationType.setText("通知")
        self.notificationContent.setText(msg)
        self.popupNotificationsContainer.setFixedHeight(104 + 22 * self.countLine(msg))
        self.popupNotificationsContainer.expandMenu()

    def message_error(self, msg):
        self.notificationType.setText("错误")
        self.notificationContent.setText(msg)
        self.popupNotificationsContainer.setFixedHeight(104 + 22 * self.countLine(msg))
        self.popupNotificationsContainer.expandMenu()

    def prepare_about(self):
        self.aboutText.setText(about)
        self.aboutText.adjustSize()

    def update(self):
        self.update_thread = UpdateThread()
        self.update_thread.updateSignal.connect(self.show_update)
        self.update_thread.start()

    def show_update(self, update_info):
        if not update_info.get('update_available'):
            self.message_notification("当前已是最新版本")
            # return
        detail = f'''当前版本:{version},最新版本:{update_info.get('latest_version')}
        更新内容:{update_info.get('description')}
        <a href='{update_info.get('download_url')}'>点击下载</a>
        '''
        self.message_notification(detail)

    def decrypt_success(self):
        self.message_notification("解密成功,请重新启动")
        self.close()

    def close(self) -> bool:
        close_db()
        super().close()
        self.exitSignal.emit(True)

    # 我的年度报告相关

    def report(self):
        time_range = ['2023-01-01 00:00:00', '2024-02-10 00:00:00']
        self.reportProgress.setText('正在生成报告\n如需查看报告请点击访问 http://127.0.0.1:21314/ 查看')
        self.report_thread = ReportThread(Me(), time_range)
        self.report_thread.start()
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:21314/"))

    # 设置相关

    def read_data(self):
        os.makedirs('./app/data', exist_ok=True)
        stopwords = ['裂开', '苦涩', '叹气', '凋谢', '让我看看', '酷', '奋斗', '疑问', '擦汗', '抠鼻', '鄙视', '勾引',
                     '奸笑', '嘿哈', '捂脸', '机智', '加油', '吃瓜', '尴尬', '炸弹', '旺柴']
        new_words = ['YYDS', '666', '显眼包', '遥遥领先']
        if os.path.exists('./app/data/stopwords.txt'):
            with open('./app/data/stopwords.txt', 'r', encoding='utf-8') as f:
                stopwords = set(f.read().splitlines())
                self.stopWordTextEdit.setPlainText(' '.join(stopwords))
        else:
            self.stopWordTextEdit.setPlainText(' '.join(stopwords))
            stopwords = '\n'.join(stopwords)
            with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
                f.write(stopwords)
        if os.path.exists('./app/data/new_words.txt'):
            with open('./app/data/new_words.txt', 'r', encoding='utf-8') as f:
                stopwords = set(f.read().splitlines())
                self.newWordTextEdit.setPlainText(' '.join(new_words))
        else:
            self.newWordTextEdit.setPlainText(' '.join(new_words))
            stopwords = '\n'.join(stopwords)
            with open('./app/data/new_words.txt', 'w', encoding='utf-8') as f:
                f.write(stopwords)

    def add_stopwords(self):
        text = self.stopWordTextEdit.toPlainText()
        stopwords = '\n'.join(text.split())
        with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
            f.write(stopwords)
        self.message_notification("停用词添加成功")

    def add_new_words(self):
        text = self.newWordTextEdit.toPlainText()
        new_words = '\n'.join(text.split())
        with open('./app/data/new_words.txt', 'w', encoding='utf-8') as f:
            f.write(new_words)
        self.message_notification("自定义词添加成功")

    def send_error_log(self):
        self.send_thread = ErrorThread()
        self.send_thread.signal.connect(self.show_resp)
        self.send_thread.start()

    def show_resp(self, msg):
        if msg.get('code') == 200:
            self.message_notification(f"日志发送成功\n{msg.get('message')}")
        else:
            self.message_notification(f"{msg.get('code')}:{msg.get('errmsg')}")

    # 自动解密相关

    def get_info(self):
        self.get_info_thread = InfoThread(self.version_list)
        self.get_info_thread.signal.connect(self.set_info)
        self.get_info_thread.start()

    def set_info(self, result):
        if result[0] == -1:
            self.message_error("请登录微信")
        elif result[0] == -2:
            self.versionErrorSignal.emit(result[1])
            self.message_error("微信版本不匹配\n请手动填写信息")

        elif result[0] == -3:
            self.message_error("WeChat WeChatWin.dll Not Found")
        elif result[0] == -10086:
            self.message_error("未知错误，请收集错误信息")
        else:
            self.ready = True
            self.info = result[0]
            self.label_key.setText(self.info['key'])
            self.lineEdit.setText(self.info['wxid'])
            self.label_name.setText(self.info['name'])
            self.label_phone.setText(self.info['mobile'])
            self.label_pid.setText(str(self.info['pid']))
            self.label_version.setText(self.info['version'])
            self.lineEdit.setFocus()
            self.getInfoCheckBox.setCheckable(True)
            self.getInfoCheckBox.setChecked(True)
            self.get_wxidSignal.emit(self.info['wxid'])
            directory = os.path.join(path.wx_path(), self.info['wxid'])
            if os.path.exists(directory):
                self.label_db_dir.setText(directory)
                self.wx_dir = directory
                self.setPathCheckBox.setCheckable(True)
                self.setPathCheckBox.setChecked(True)
                self.ready = True
            if self.ready:
                self.label_ready.setText('已就绪')
            if self.wx_dir and os.path.exists(os.path.join(self.wx_dir)):
                self.label_ready.setText('已就绪')

    def set_wxid_(self):
        self.info['wxid'] = self.lineEdit.text()

    def set_wxid(self):
        self.info['wxid'] = self.lineEdit.text()
        self.message_notification("wxid修改成功")

    def select_db_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选取微信文件保存目录——能看到Msg文件夹",
            path.wx_path()
        )
        db_dir = os.path.join(directory, 'Msg')
        if not os.path.exists(db_dir):
            self.message_error("文件夹选择错误\n一般以wxid_xxx结尾")
            return

        self.label_db_dir.setText(directory)
        self.wx_dir = directory
        self.setPathCheckBox.setCheckable(True)
        self.setPathCheckBox.setChecked(True)
        if self.ready:
            self.label_ready.setText('已就绪')

    def decrypt(self):
        if not self.ready:
            self.message_error("请先获取信息")
            return
        if not self.wx_dir:
            self.message_error("请先选择微信安装路径")
            return
        if self.lineEdit.text() == 'None':
            self.message_error("请填入wxid")
            return
        db_dir = os.path.join(self.wx_dir, 'Msg')
        if self.ready:
            if not os.path.exists(db_dir):
                self.message_error("文件夹选择错误\n一般以wxid_xxx结尾")
                return
        if self.info.get('key') == 'None':
            self.message_error("密钥错误\n请查看教程解决相关问题")
        close_db()
        self.thread2 = DecryptThread(db_dir, self.info['key'])
        self.thread2.maxNumSignal.connect(self.setProgressBarMaxNum)
        self.thread2.signal.connect(self.progressBar_view)
        self.thread2.okSignal.connect(self.btnExitClicked)
        self.thread2.errorSignal.connect(
            lambda x: self.message_error("错误\n请检查微信版本是否为最新和微信路径是否正确\n或者关闭微信多开")
        )
        self.thread2.start()

    def btnEnterClicked(self):
        self.progressBar_view(self.max_val)
        self.DecryptSignal.emit(True)

    def setProgressBarMaxNum(self, max_val):
        self.max_val = max_val
        self.progressBar.setRange(0, max_val)

    def progressBar_view(self, value):
        self.progressBar.setProperty('value', value)

    def btnExitClicked(self):
        dic = {
            'wxid': self.info['wxid'],
            'wx_dir': self.wx_dir,
            'name': self.info['name'],
            'mobile': self.info['mobile']
        }
        try:
            with open(INFO_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(dic, f, ensure_ascii=False, indent=4)
        except:
            with open('./info.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(dic))
        self.progressBar_view(self.max_val)
        self.DecryptSignal.emit(True)
        self.close()

    # 手动解密相关

    def upload(self, version_data):
        url = urljoin(SERVER_API_URL, 'wxBiasAddr')
        try:
            requests.post(url, json=version_data)
            print('版本信息上传成功')
        except:
            pass

    def get_bias_addr(self):
        account = self.lineEdit_wx_alias.text()
        mobile = self.lineEdit_tel.text()
        name = self.lineEdit_wx_name.text()
        if not all([account, mobile, name]):
            self.message_error("请把所有信息填写完整")
            return
        key = None
        db_path = "test"
        self.thread = BiasThread(account, mobile, name, key, db_path)
        self.thread.signal.connect(self.set_bias_addr)
        self.thread.start()

    def set_bias_addr(self, data):
        self.upload(data)
        self.biasAddrSignal.emit(data)

    # 好友相关
    
    def statistic(self):
        self.friendView.stackedWidget.currentWidget().analysis()
        
    def mood(self):
        self.friendView.stackedWidget.currentWidget().emotionale_Analysis()
        
    def user_report(self):
        self.friendView.stackedWidget.currentWidget().annual_report()
        
    # 数据导出相关
    
    def set_export_date(self):
        date_range = self.comboBox_time.currentText()
        if date_range == '全部时间':
            pass
        elif date_range == '最近三个月':
            from datetime import datetime, timedelta
            today = datetime.now()
            today_date = today.date()
            today_midnight = datetime.combine(today_date, datetime.min.time()) + timedelta(days=1)
            today_midnight_timestamp = int(today_midnight.timestamp())
            three_months_ago = today - timedelta(days=90)
            three_months_ago_date = three_months_ago.date()
            three_months_ago_midnight = datetime.combine(three_months_ago_date, datetime.min.time())
            three_months_ago_midnight_timestamp = int(three_months_ago_midnight.timestamp())
            self.time_range = (three_months_ago_midnight_timestamp, today_midnight_timestamp)

        elif date_range == '自定义时间':
            self.time_range_view = TimeRangeDialog(parent=self)
            self.time_range_view.date_range_signal.connect(self.set_time_range)
            self.time_range_view.show()
            self.comboBox_time.setCurrentIndex(0)

    def set_time_range(self, time_range):
        self.time_range = time_range
        self.comboBox_time.setCurrentIndex(2)

    def export_data(self):
        self.exportBatchBtn.setEnabled(False)
        selected_types = {export_types[export_type]: checkbox.isChecked() for export_type, checkbox in
                          zip(self.export_choices.keys(), self.findChildren(QCheckBox, 'message_type'))}
        print("选择的数据类型:", selected_types)

        file_types = []
        for checkbox in [self.checkBox_txt, self.checkBox_csv, self.checkBox_html, self.checkBox_word]:
            if checkbox.isChecked():
                file_types.append(export_file_format[checkbox.text()])
        select_contacts = []
        count = self.listWidget.count()
        for i in range(count):
            item = self.listWidget.item(i)
            if item.is_select:
                select_contacts.append(self.contacts[i])
        print("选择的文件格式:", file_types)
        self.worker = Output(select_contacts, type_=Output.Batch, message_types=selected_types, sub_type=file_types,
                             time_range=self.time_range)
        self.worker.okSignal.connect(self.export_finished)
        self.worker.rangeSignal.connect(self.set_total_msg_num)
        self.worker.nowContact.connect(self.update_progress)
        self.worker.start()
        self.timer.start(1000)
        self.start_time = time.time()

    def set_total_msg_num(self, num):
        self.total_msg_num = num

    def setCurrentIndex(self, item):
        item.select()
        item.dis_select()

    def select_all(self):
        self.select_all_flag = not self.select_all_flag
        print('全选', self.select_all_flag)
        if self.select_all_flag:
            count = self.listWidget.count()
            for i in range(count):
                item = self.listWidget.item(i)
                item.force_select()
            self.btn_select_all.setText('全不选')
        else:
            count = self.listWidget.count()
            for i in range(count):
                item = self.listWidget.item(i)
                item.force_dis_select()
            self.btn_select_all.setText('全选')

    def export_finished(self):
        self.exportBatchBtn.setEnabled(True)
        self.time = 0
        end_time = time.time()
        print(f'总耗时:{end_time - self.start_time}s')
        self.message_notification(f"导出聊天记录成功\n在{OUTPUT_DIR}目录下(跟exe文件在一起)\n{os.path.normpath(os.path.join(os.getcwd(), OUTPUT_DIR))}")

    def show_contact(self, contact):
        contact_item = ContactQListWidgetItem(contact.remark, contact.smallHeadImgUrl, contact.smallHeadImgBLOG)
        self.listWidget.addItem(contact_item)
        self.listWidget.setItemWidget(contact_item, contact_item.widget)
        self.contacts.append(contact)

    def update_elapsed_time(self):
        self.time += 1
        self.label_time.setText(f"耗时: {self.time}s")

    def update_progress(self, remark):
        self.num += 1
        progress_percentage = int((self.num) / self.total_msg_num * 100)
        self.exportProgressBar.setValue(progress_percentage)
        self.label_process.setText(f"导出进度: {progress_percentage}% {remark}")