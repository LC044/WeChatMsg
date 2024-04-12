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
import time
import traceback
from urllib.parse import urljoin

import requests
from PyQt5.QtCore import pyqtSignal, QThread, QSize, QUrl, Qt
from PyQt5.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QPushButton

from app.DataBase import misc_db, micro_msg_db, close_db
from app.ui.Icon import Icon
from . import mainwindow
# 不能删，删了会出错
from app.ui.chat import ChatWindow
from app.ui.contact import ContactWindow
from app.ui.tool.tool_window import ToolWindow
from app.ui.home.home_window import HomeWindow
from .menu.export import ExportDialog
from app.util.exporter.output import Output
from ..components.QCursorGif import QCursorGif
from ..config import INFO_FILE_PATH, DB_DIR, SERVER_API_URL, version
from ..log import logger
from ..person import Me

try:
    from app.ui.menu.about_dialog import AboutDialog
except ModuleNotFoundError:
    logger.error(f'Python版本错误:Python>=3.10,仅支持3.10、3.11、3.12')
    raise ValueError('Python版本错误:Python>=3.10,仅支持3.10、3.11、3.12')
# 美化样式表
Stylesheet = """
QMessageBox QPushButton{
    background-color: rgb(250,252,253);
    border-radius: 5px;
    padding: 8px;
    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
}
QPushButton{
    background-color: rgb(238,244,249);
    border-radius: 5px;
    padding: 8px;
}
QPushButton:hover { 
    background-color: lightgray;
}
QWidget{
    background: rgb(238,244,249);
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
}

QMenu::item:selected {
      color: black;
      background: rgb(230, 235, 240);
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 120px;
    max-width: 380px;
    color: black;
    border:none;
}
QListWidget::item{
    min-width: 80px;
    max-width: 380px;
    min-height: 60px;
    max-height: 60px;
}
QListWidget::item:hover {
    background: rgb(230, 235, 240);
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    background: rgb(230, 235, 240);
    border-left: 2px solid rgb(62, 62, 62);
    color: black;
    font-weight: bold;
}
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
}

QCheckBox::indicator {
    background: rgb(255, 255, 255);
    Width:20px;
    Height:20px;
    border-radius: 10px
}
QCheckBox::indicator:unchecked{
    Width:20px;
    Height:20px;
    image: url(:/icons/icons/unselect.svg);
}
QCheckBox::indicator:checked{
    Width:20px;
    Height:20px;
    image: url(:/icons/icons/select.svg);
}
QScrollBar:vertical {
    border-width: 0px;
    border: none;
    background:rgba(133, 135, 138, 0);
    width:4px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0 rgb(133, 135, 138), stop: 0.5 rgb(133, 135, 138), stop:1 rgb(133, 135, 138));
    min-height: 20px;
    max-height: 20px;
    margin: 0 0px 0 0px;
    border-radius: 2px;
}
QScrollBar::add-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0 rgba(133, 135, 138, 0), stop: 0.5 rgba(133, 135, 138, 0),  stop:1 rgba(133, 135, 138, 0));
    height: 0px;
    border: none;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0  rgba(133, 135, 138, 0), stop: 0.5 rgba(133, 135, 138, 0),  stop:1 rgba(133, 135, 138, 0));
    height: 0 px;
    border: none;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QScrollBar::sub-page:vertical {
    background: rgba(133, 135, 138, 0);
}

QScrollBar::add-page:vertical {
    background: rgba(133, 135, 138, 0);
}
QProgressBar{
    height:22px; 
    text-align:center; 
    font-size:14px; 
    color:black;
    border-radius:11px; 
    background:#EBEEF5;
}
QProgressBar::chunk{
    border-radius:11px;
    background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #99ffff,stop:1 #9900ff);
}
QComboBox
{
    border-radius:3px;
    border:0px ;
    padding-top: 2px;
    padding-left: 2px;
}
QComboBox:disabled
{
    background-color:rgba(50,50,50,200);
    color:rgb(160,160,160);
}
QComboBox:hover
{
    background-color:rgba(230,230,230,200);
    border:1px solid rgb(31,156,220) ;
}
 /*下拉箭头的边框*/
QComboBox::drop-down 
{
    border:none;
}

 /*下拉箭头样式*/
QComboBox::down-arrow 
{
    right:0px;/*控制箭头左右偏移*/
    width: 16px;  
    height: 16px;   
    image: url(:/icons/icons/down.svg);
}
 /*下拉箭头点击样式*/
QComboBox::down-arrow:on
{
    width: 16px;  
    height: 16px;   
    image: url(:/icons/icons/up.svg);
}
QLineEdit
{
    background:transparent;
    border-radius:10px;
    border-top: 0px solid #b2e281;
    border-bottom: 1px solid rgb(227,228,222);
    border-right: 1px solid rgb(227,228,222);
    border-left: 0px solid #b2e281;
    border-style:outset;
    background-color:rgb(247,248,252);
}
QLineEdit:hover
{
    background-color:rgb(238,241,248);
}
"""

'''


/*点击combox的样式*/
QComboBox:on
{
	border-radius:3px;
	background-color:rgba(35,35,35);
	font: 75 9pt "Microsoft YaHei";
    color:rgb(255,255,255);
    border:1px solid rgb(31,156,220) ;
}
/*下拉框的样式*/
QComboBox QAbstractItemView 
{
    outline: 0px solid gray;  /*取消选中虚线*/
    border: 1px solid rgb(31,156,220);  
    font: 75 9pt "Microsoft YaHei";
    color: rgb(255,255,255);
    background-color: rgb(45,45,45);   
    selection-background-color: rgb(90,90,90);   
}
 /*选中每一项高度*/
QComboBox QAbstractItemView::item
 { 
    height: 25px;  
 }
/*选中每一项的字体颜色和背景颜色*/
QComboBox QAbstractItemView::item:selected 
{
    color: rgb(31,163,246);
    background-color: rgb(90,90,90); 
}

'''


class Avatar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, e):  # 双击
        super().mouseDoubleClickEvent()
        QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7"))

    def mousePressEvent(self, e):  # 单击
        super().mousePressEvent(e)
        QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/7"))


class MainWinController(QMainWindow, mainwindow.Ui_MainWindow, QCursorGif):
    exitSignal = pyqtSignal(bool)
    okSignal = pyqtSignal(bool)

    # username = ''
    def __init__(self, username, parent=None):
        super(MainWinController, self).__init__(parent)
        self.outputThread0 = None
        self.outputThread = None
        self.setupUi(self)
        # self.myavatar = Avatar(self)
        # self.setWindowIcon(Icon.MainWindow_Icon)
        pixmap = QPixmap(Icon.logo_ico_path)
        icon = QIcon(pixmap)
        self.setWindowIcon(icon)
        self.setStyleSheet(Stylesheet)
        self.listWidget.clear()
        self.resize(QSize(800, 600))
        self.info = QLabel(self)
        self.info.setText('Tips ')
        self.info.setAlignment(Qt.AlignRight)
        self.statusbar.addPermanentWidget(self.info)
        self.statusbar.showMessage('遇到问题可添加QQ群咨询', 5000)
        self.load_flag = False
        self.load_data()
        self.load_num = 0
        self.label = QLabel(self)
        self.label.setGeometry((self.width() - 300) // 2, (self.height() - 100) // 2, 300, 100)
        self.label.setPixmap(QPixmap(':/icons/icons/loading.svg'))
        self.menu_output.setIcon(Icon.Output)
        self.action_output_CSV.setIcon(Icon.ToCSV)
        self.action_output_CSV.triggered.connect(self.output)
        self.action_output_contacts.setIcon(Icon.Output)
        self.action_output_contacts.triggered.connect(self.output)
        self.action_batch_export.setIcon(Icon.Output)
        self.action_batch_export.triggered.connect(self.output)
        self.action_desc.setIcon(Icon.Help_Icon)
        self.action_update.setIcon(Icon.Update_Icon)

    def load_data(self, flag=True):
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

    def init_ui(self):
        # 设置忙碌光标图片数组
        self.initCursor([':/icons/icons/Cursors/%d.png' %
                         i for i in range(8)])
        self.setCursorTimeout(100)
        self.startBusy()
        self.action_update.triggered.connect(self.update)
        self.action_help_faq.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://memotrace.cn/doc/posts/error/")))
        self.about_view = AboutDialog(main_window=self, parent=self)
        self.update_thread = UpdateThread(check_time=True)
        self.update_thread.updateSignal.connect(self.show_update)
        self.update_thread.start()

    def setCurrentIndex(self, row):
        self.stackedWidget.setCurrentIndex(row)
        if row == 2:
            self.stackedWidget.currentWidget().show_contacts()
        if row == 1:
            self.stackedWidget.currentWidget().show_chats()

    def setWindow(self, window):
        try:
            window.load_finish_signal.connect(self.loading)
        except:
            pass
        self.stackedWidget.addWidget(window)

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
            QMessageBox.critical(self, "数据库错误", "数据库错误，请删除app文件夹后重启电脑再运行软件")
            return
        me = Me()
        me.set_avatar(img_bytes)
        me.smallHeadImgUrl = contact_info_list[7]
        self.myavatar.setScaledContents(True)
        self.myavatar.setPixmap(self.avatar)

    def stop_loading(self, a0):
        self.label.setVisible(False)
        self.stopBusy()

    def loading(self, a0):
        self.load_num += 1
        if self.load_num == 1:
            self.label.clear()
            self.label.hide()
            self.okSignal.emit(True)
            self.listWidget.setVisible(True)
            self.stackedWidget.setVisible(True)
            self.stopBusy()
            if self.load_flag:
                self.listWidget.setCurrentRow(1)
                self.stackedWidget.setCurrentIndex(1)
            else:
                self.listWidget.setCurrentRow(0)
                self.stackedWidget.setCurrentIndex(0)

    def output(self):
        # self.startBusy()
        if self.sender() == self.action_output_CSV:
            self.outputThread = Output(None, type_=Output.CSV_ALL)
            self.outputThread.startSignal.connect(lambda x: self.startBusy())
            self.outputThread.okSignal.connect(
                lambda x: self.message('聊天记录导出成功'))
            self.outputThread.start()
        elif self.sender() == self.action_output_contacts:
            self.outputThread = Output(None, type_=Output.CONTACT_CSV)
            self.outputThread.startSignal.connect(lambda x: self.startBusy())
            self.outputThread.okSignal.connect(
                lambda x: self.message('联系人导出成功'))
            self.outputThread.start()
        elif self.sender() == self.action_batch_export:
            dialog = ExportDialog(None, title='批量导出聊天记录', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果

    def message(self, msg):
        self.stopBusy()
        QMessageBox.about(self, "提醒", msg)

    def update(self):
        self.update_thread = UpdateThread()
        self.update_thread.updateSignal.connect(self.show_update)
        self.update_thread.start()

    def show_update(self, update_info):
        if not update_info.get('update_available'):
            QMessageBox.information(self, '更新通知', "当前已是最新版本")
            return
        detail = f'''
        当前版本:{version},最新版本:{update_info.get('latest_version')}<br>
        更新内容:
        {update_info.get('description')}
        <br><a href='https://memotrace.cn/'>查看详情</a>
        '''

        # 创建一个 QMessageBox 对象
        error_box = QMessageBox()

        # 设置对话框的标题
        error_box.setWindowTitle("更新通知")
        pixmap = QPixmap(Icon.logo_ico_path)
        icon = QIcon(pixmap)
        error_box.setWindowIcon(icon)
        # 设置对话框的文本消息
        error_box.setText(detail)
        # 设置对话框的图标，使用 QMessageBox.Critical 作为图标类型
        error_box.setIcon(QMessageBox.Information)
        # 添加一个“确定”按钮
        # 添加自定义按钮
        custom_button = error_box.addButton('更新', QMessageBox.ActionRole)
        is_update_online = update_info.get('is_update_online')
        custom_button.clicked.connect(lambda x: self.update_(update_info.get('download_url'), is_update_online))
        error_box.addButton(QMessageBox.Cancel)
        # 显示对话框
        error_box.exec_()

    def update_(self, url, is_update_online):
        QDesktopServices.openUrl(QUrl("https://memotrace.cn/"))

    def about(self):
        """
        关于
        """
        self.about_view.show()

    def decrypt_success(self):
        QMessageBox.about(self, "解密成功", "请重新启动")
        self.close()

    def closeEvent(self, event):
        close_db()

    def close(self) -> bool:
        close_db()
        self.contact_window.close()

        super().close()
        self.exitSignal.emit(True)


class UpdateThread(QThread):
    updateSignal = pyqtSignal(dict)

    def __init__(self, check_time=False):
        super().__init__()
        self.check_time = check_time

    def run(self):
        now_time = time.time()
        try:
            with open(INFO_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            update_time = data.get('update_time')
            if update_time:
                if now_time - update_time < 14400 and self.check_time:
                    return
        except:
            os.makedirs(os.path.dirname(INFO_FILE_PATH), exist_ok=True)
            data = {
                'update_time': now_time
            }
        data['update_time'] = now_time

        with open(INFO_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        server_url = urljoin(SERVER_API_URL, 'update')
        data = {'version': version}
        try:
            response = requests.post(server_url, json=data)
            if response.status_code == 200:
                update_info = response.json()
                self.updateSignal.emit(update_info)
            else:
                print("检查更新失败")
        except:
            update_info = {'update_available': False}
            self.updateSignal.emit(update_info)
