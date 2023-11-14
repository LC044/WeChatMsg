import os.path
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.decrypt import get_wx_info, decrypt
from . import decryptUi


class DecryptControl(QWidget, decryptUi.Ui_Dialog):
    DecryptSignal = pyqtSignal(str)
    registerSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DecryptControl, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('解密')
        self.setWindowIcon(QIcon('./app/data/icons/logo.svg'))
        self.pushButton_3.clicked.connect(self.decrypt)
        self.btn_getinfo.clicked.connect(self.get_info)
        self.btn_db_dir.clicked.connect(self.select_db_dir)
        self.info = {}
        self.lineEdit.setFocus()
        self.ready = False
        self.wx_dir = None

    # @log
    def get_info(self):
        try:
            result = get_wx_info.get_info()
            if result == -1:
                QMessageBox.critical(self, "错误", "请登录微信")
            elif result == -2:
                QMessageBox.critical(self, "错误", "微信版本不匹配\n请更新微信版本为:3.9.8.15")
            # print(result)
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
                if self.wx_dir and os.path.exists(os.path.join(self.wx_dir, self.info['wxid'])):
                    self.label_ready.setText('已就绪')
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "错误", "请登录微信")

    def select_db_dir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选取微信安装目录——能看到All Users文件夹",
            "C:/")  # 起始路径
        if directory:
            self.label_db_dir.setText(directory)
            self.wx_dir = directory
            if self.ready:
                self.label_ready.setText('已就绪')

    def decrypt(self):
        if not self.ready:
            QMessageBox.critical(self, "错误", "请先获取密钥")
            return
        if not self.wx_dir:
            QMessageBox.critical(self, "错误", "请先选择微信安装路径")
            return
        if self.lineEdit.text() == 'None':
            QMessageBox.critical(self, "错误", "请填入wxid")
            return
        if self.ready:
            if not os.path.exists(os.path.join(self.wx_dir, self.info['wxid'])):
                QMessageBox.critical(self, "错误", "文件夹选择错误\n一般以WeChat Files结尾")
                return
        db_dir = os.path.join(self.wx_dir, self.info['wxid'], 'Msg')
        self.thread2 = DecryptThread(db_dir, self.info['key'])
        self.thread2.maxNumSignal.connect(self.setProgressBarMaxNum)
        self.thread2.signal.connect(self.progressBar_view)
        self.thread2.okSignal.connect(self.btnExitClicked)
        self.thread2.start()

    def btnEnterClicked(self):
        # print("enter clicked")
        # 中间可以添加处理逻辑
        # QMessageBox.about(self, "解密成功", "数据库文件存储在app/DataBase/Msg文件夹下")
        self.DecryptSignal.emit('ok')
        self.close()

    def setProgressBarMaxNum(self, max_val):
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
        self.DecryptSignal.emit('ok')
        self.close()


class DecryptThread(QThread):
    signal = pyqtSignal(str)
    maxNumSignal = pyqtSignal(int)
    okSignal = pyqtSignal(str)

    def __init__(self, db_path, key):
        super(DecryptThread, self).__init__()
        self.db_path = db_path
        self.key = key
        self.textBrowser = None

    def __del__(self):
        pass

    def run(self):
        # data.decrypt(self.db_path, self.key)
        output_dir = 'app/DataBase/Msg'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        tasks = []
        if os.path.exists(self.db_path):
            for root, dirs, files in os.walk(self.db_path):
                for file in files:
                    if '.db' == file[-3:]:
                        inpath = os.path.join(root, file)
                        # print(inpath)
                        output_path = os.path.join(output_dir, file)
                        tasks.append([self.key, inpath, output_path])
        self.maxNumSignal.emit(len(tasks))
        for i, task in enumerate(tasks):
            decrypt.decrypt(*task)
            self.signal.emit(str(i + 1))
        # print(self.db_path)
        self.okSignal.emit('ok')
        # self.signal.emit('100')


class MyThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(MyThread, self).__init__()

    def __del__(self):
        pass

    def run(self):
        for i in range(100):
            self.signal.emit(str(i))
            time.sleep(0.1)
