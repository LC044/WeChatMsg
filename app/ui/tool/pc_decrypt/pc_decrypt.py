import json
import os.path
import sys
import traceback

import requests
from PyQt5.QtCore import pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog

from app.DataBase import msg_db, misc_db, close_db
from app.DataBase.merge import merge_databases, merge_MediaMSG_databases
from app.components.QCursorGif import QCursorGif
from app.config import info_file_path, db_dir
from app.decrypt import get_wx_info, decrypt
from app.log import logger
from app.util import path
from . import decryptUi
from ...Icon import Icon


class DecryptControl(QWidget, decryptUi.Ui_Dialog, QCursorGif):
    DecryptSignal = pyqtSignal(bool)
    get_wxidSignal = pyqtSignal(str)
    versionErrorSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DecryptControl, self).__init__(parent)
        self.max_val = 0
        self.setupUi(self)
        # 设置忙碌光标图片数组
        self.initCursor([':/icons/icons/Cursors/%d.png' %
                         i for i in range(8)], self)
        self.setCursorTimeout(100)
        self.version_list = None
        self.btn_start.clicked.connect(self.decrypt)
        self.btn_getinfo.clicked.connect(self.get_info)
        self.btn_db_dir.clicked.connect(self.select_db_dir)
        self.lineEdit.returnPressed.connect(self.set_wxid)
        self.lineEdit.textChanged.connect(self.set_wxid_)
        self.btn_help.clicked.connect(self.show_help)
        self.btn_getinfo.setIcon(Icon.Get_info_Icon)
        self.btn_db_dir.setIcon(Icon.Folder_Icon)
        self.btn_start.setIcon(Icon.Start_Icon)
        self.btn_help.setIcon(Icon.Help_Icon)
        self.info = {}
        self.lineEdit.setFocus()
        self.ready = False
        self.wx_dir = None

    def show_help(self):
        # 定义网页链接
        url = QUrl("https://blog.lc044.love/post/4")
        # 使用QDesktopServices打开网页
        QDesktopServices.openUrl(url)

    # @log
    def get_info(self):
        self.startBusy()
        self.get_info_thread = MyThread(self.version_list)
        self.get_info_thread.signal.connect(self.set_info)
        self.get_info_thread.start()

    def set_info(self, result):
        # print(result)
        if result[0] == -1:
            QMessageBox.critical(self, "错误", "请登录微信")
        elif result[0] == -2:
            self.versionErrorSignal.emit(result[1])
            QMessageBox.critical(self, "错误",
                                 "微信版本不匹配\n请手动填写信息")

        elif result[0] == -3:
            QMessageBox.critical(self, "错误", "WeChat WeChatWin.dll Not Found")
        elif result[0] == -10086:
            QMessageBox.critical(self, "错误", "未知错误，请收集错误信息")
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
            self.checkBox.setCheckable(True)
            self.checkBox.setChecked(True)
            self.get_wxidSignal.emit(self.info['wxid'])
            directory = os.path.join(path.wx_path(), self.info['wxid'])
            if os.path.exists(directory):
                self.label_db_dir.setText(directory)
                self.wx_dir = directory
                self.checkBox_2.setCheckable(True)
                self.checkBox_2.setChecked(True)
                self.ready = True
            if self.ready:
                self.label_ready.setText('已就绪')
            if self.wx_dir and os.path.exists(os.path.join(self.wx_dir)):
                self.label_ready.setText('已就绪')
        self.stopBusy()

    def set_wxid_(self):
        self.info['wxid'] = self.lineEdit.text()

    def set_wxid(self):
        self.info['wxid'] = self.lineEdit.text()
        QMessageBox.information(self, "ok", f"wxid修改成功{self.info['wxid']}")

    def select_db_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选取微信文件保存目录——能看到Msg文件夹",
            path.wx_path()
        )  # 起始路径
        db_dir = os.path.join(directory, 'Msg')
        if not os.path.exists(db_dir):
            QMessageBox.critical(self, "错误", "文件夹选择错误\n一般以wxid_xxx结尾")
            return

        self.label_db_dir.setText(directory)
        self.wx_dir = directory
        self.checkBox_2.setCheckable(True)
        self.checkBox_2.setChecked(True)
        if self.ready:
            self.label_ready.setText('已就绪')

    def decrypt(self):
        if not self.ready:
            QMessageBox.critical(self, "错误", "请先获取信息")
            return
        if not self.wx_dir:
            QMessageBox.critical(self, "错误", "请先选择微信安装路径")
            return
        if self.lineEdit.text() == 'None':
            QMessageBox.critical(self, "错误", "请填入wxid")
            return
        db_dir = os.path.join(self.wx_dir, 'Msg')
        if self.ready:
            if not os.path.exists(db_dir):
                QMessageBox.critical(self, "错误", "文件夹选择错误\n一般以wxid_xxx结尾")
                return
        if self.info.get('key') == 'None':
            QMessageBox.critical(self, "错误",
                                 "密钥错误\n请查看教程解决相关问题")
        close_db()
        self.thread2 = DecryptThread(db_dir, self.info['key'])
        self.thread2.maxNumSignal.connect(self.setProgressBarMaxNum)
        self.thread2.signal.connect(self.progressBar_view)
        self.thread2.okSignal.connect(self.btnExitClicked)
        self.thread2.errorSignal.connect(
            lambda x: QMessageBox.critical(self, "错误",
                                           "错误\n请检查微信版本是否为最新和微信路径是否正确\n或者关闭微信多开")
        )
        self.thread2.start()

    def btnEnterClicked(self):
        # print("enter clicked")
        # 中间可以添加处理逻辑
        # QMessageBox.about(self, "解密成功", "数据库文件存储在app/DataBase/Msg文件夹下")
        self.progressBar_view(self.max_val)
        self.DecryptSignal.emit(True)
        # self.close()

    def setProgressBarMaxNum(self, max_val):
        self.max_val = max_val
        self.progressBar.setRange(0, max_val)

    def progressBar_view(self, value):
        """
        进度条显示
        :param value: 进度0-100
        :return: None
        """
        self.progressBar.setProperty('value', value)
        #     self.btnExitClicked()
        #     data.init_database()

    def btnExitClicked(self):
        # print("Exit clicked")
        dic = {
            'wxid': self.info['wxid'],
            'wx_dir': self.wx_dir,
            'name': self.info['name'],
            'mobile': self.info['mobile']
        }

        try:
            os.makedirs('./app/data', exist_ok=True)
            with open(info_file_path, "w", encoding="utf-8") as f:
                json.dump(dic, f, ensure_ascii=False, indent=4)
        except:
            with open('./info.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(dic))
        self.progressBar_view(self.max_val)
        self.DecryptSignal.emit(True)
        self.close()


class DecryptThread(QThread):
    signal = pyqtSignal(str)
    maxNumSignal = pyqtSignal(int)
    okSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(bool)

    def __init__(self, db_path, key):
        super(DecryptThread, self).__init__()
        self.db_path = db_path
        self.key = key
        self.textBrowser = None

    def __del__(self):
        pass

    def run(self):
        misc_db.close()
        msg_db.close()
        # micro_msg_db.close()
        # hard_link_db.close()
        output_dir = db_dir
        os.makedirs(output_dir, exist_ok=True)
        tasks = []
        if os.path.exists(self.db_path):
            for root, dirs, files in os.walk(self.db_path):
                for file in files:
                    if '.db' == file[-3:]:
                        if 'xInfo.db' == file:
                            continue
                        inpath = os.path.join(root, file)
                        # print(inpath)
                        output_path = os.path.join(output_dir, file)
                        tasks.append([self.key, inpath, output_path])
        self.maxNumSignal.emit(len(tasks))
        for i, task in enumerate(tasks):
            if decrypt.decrypt(*task) == -1:
                self.errorSignal.emit(True)
            self.signal.emit(str(i))
        # print(self.db_path)
        # 目标数据库文件
        target_database = os.path.join(db_dir, 'MSG.db')
        # 源数据库文件列表
        source_databases = [os.path.join(db_dir, f"MSG{i}.db") for i in range(1, 50)]
        import shutil
        if os.path.exists(target_database):
            os.remove(target_database)
        try:
            shutil.copy2(os.path.join(db_dir, 'MSG0.db'), target_database)  # 使用一个数据库文件作为模板
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            self.errorSignal.emit(True)
        # 合并数据库
        try:
            merge_databases(source_databases, target_database)
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            QMessageBox.critical("错误", "数据库不存在\n请检查微信版本是否为最新")

        # 音频数据库文件
        target_database = os.path.join(db_dir,'MediaMSG.db')
        # 源数据库文件列表
        if os.path.exists(target_database):
            os.remove(target_database)
        source_databases = [os.path.join(db_dir,f"MediaMSG{i}.db") for i in range(1, 50)]
        try:
            shutil.copy2(os.path.join(db_dir,'MediaMSG0.db'), target_database)  # 使用一个数据库文件作为模板
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            self.errorSignal.emit(True)
        # 合并数据库
        try:
            merge_MediaMSG_databases(source_databases, target_database)
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            QMessageBox.critical("错误", "数据库不存在\n请检查微信版本是否为最新")
        self.okSignal.emit('ok')
        # self.signal.emit('100')


class MyThread(QThread):
    signal = pyqtSignal(list)

    def __init__(self, version_list=None):
        super(MyThread, self).__init__()
        self.version_list = version_list

    def __del__(self):
        pass

    def get_bias_add(self, version):
        url = "http://api.lc044.love/wxBiasAddr"
        data = {
            'version': version
        }
        try:
            response = requests.get(url, json=data)
            print(response)
            print(response.text)
            if response.status_code == 200:
                update_info = response.json()
                return update_info
            else:
                return {}
        except:
            return {}

    def run(self):
        if self.version_list:
            VERSION_LIST = self.version_list
        else:
            file_path = './app/resources/data/version_list.json'
            if not os.path.exists(file_path):
                resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
                file_path = os.path.join(resource_dir, 'app', 'resources', 'data', 'version_list.json')
            with open(file_path, "r", encoding="utf-8") as f:
                VERSION_LIST = json.loads(f.read())
        try:
            result = get_wx_info.get_info(VERSION_LIST)
            if result == -1:
                result = [result]
            elif result == -2:
                result = [result]
            elif result == -3:
                result = [result]
            elif isinstance(result, str):
                version = result
                # version = '3.9.9.43'
                version_bias = self.get_bias_add(version)
                if version_bias.get(version):
                    logger.info(f"从云端获取内存基址:{version_bias}")
                    result = get_wx_info.get_info(version_bias)
                else:
                    logger.info(f"从云端获取内存基址失败:{version}")
                    result = [-2, version]
        except:
            logger.error(traceback.format_exc())
            result = [-10086]
        self.signal.emit(result)
