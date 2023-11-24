import json
import os.path
import time
import traceback

from PyQt5.QtCore import pyqtSignal, QThread, QUrl, QFile, QIODevice, QTextStream
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog

from app.decrypt import get_wx_info, decrypt
from app.log import logger
from . import decryptUi


class DecryptControl(QWidget, decryptUi.Ui_Dialog):
    DecryptSignal = pyqtSignal(bool)
    get_wxidSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DecryptControl, self).__init__(parent)
        self.setupUi(self)

        self.pushButton_3.clicked.connect(self.decrypt)
        self.btn_getinfo.clicked.connect(self.get_info)
        self.btn_db_dir.clicked.connect(self.select_db_dir)
        self.lineEdit.returnPressed.connect(self.set_wxid)
        self.lineEdit.textChanged.connect(self.set_wxid_)
        self.btn_help.clicked.connect(self.show_help)
        self.info = {}
        self.lineEdit.setFocus()
        self.ready = False
        self.wx_dir = None

    def show_help(self):
        # 定义网页链接
        url = QUrl("http://8.146.206.114/post/4")

        # 使用QDesktopServices打开网页
        QDesktopServices.openUrl(url)

    # @log
    def get_info(self):
        try:
            file = QFile(':/data/version_list.json')
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                stream = QTextStream(file)
                content = stream.readAll()
                file.close()
                VERSION_LIST = json.loads(content)
            else:
                return
            result = get_wx_info.get_info(VERSION_LIST)
            print(result)
            if result == -1:
                QMessageBox.critical(self, "错误", "请登录微信")
            elif result == -2:
                QMessageBox.critical(self, "错误", "微信版本不匹配\n请更新微信版本为:3.9.8.15")
            elif result == -3:
                QMessageBox.critical(self, "错误", "WeChat WeChatWin.dll Not Found")
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
                self.checkBox.setChecked(True)
                self.get_wxidSignal.emit(self.info['wxid'])
                if self.wx_dir and os.path.exists(os.path.join(self.wx_dir)):
                    self.label_ready.setText('已就绪')
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "错误", "请登录微信")
            logger.error(traceback.format_exc())
            traceback.print_exc()

    def set_wxid_(self):
        self.info['wxid'] = self.lineEdit.text()

    def set_wxid(self):
        self.info['wxid'] = self.lineEdit.text()
        QMessageBox.information(self, "ok", f"wxid修改成功{self.info['wxid']}")

    def select_db_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选取微信安装目录——能看到Msg文件夹",
            "C:/")  # 起始路径
        db_dir = os.path.join(directory, 'Msg')
        if not os.path.exists(db_dir):
            QMessageBox.critical(self, "错误", "文件夹选择错误\n一般以wxid_xxx结尾")
            return

        self.label_db_dir.setText(directory)
        self.wx_dir = directory
        self.checkBox_2.setChecked(True)
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
        db_dir = os.path.join(self.wx_dir, 'Msg')
        if self.ready:
            if not os.path.exists(db_dir):
                QMessageBox.critical(self, "错误", "文件夹选择错误\n一般以wxid_xxx结尾")
                return

        self.thread2 = DecryptThread(db_dir, self.info['key'])
        self.thread2.maxNumSignal.connect(self.setProgressBarMaxNum)
        self.thread2.signal.connect(self.progressBar_view)
        self.thread2.okSignal.connect(self.btnExitClicked)
        self.thread2.start()

    def btnEnterClicked(self):
        # print("enter clicked")
        # 中间可以添加处理逻辑
        # QMessageBox.about(self, "解密成功", "数据库文件存储在app/DataBase/Msg文件夹下")

        self.DecryptSignal.emit(True)
        # self.close()

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
        dic = {
            'wxid': self.info['wxid'],
            'wx_dir': self.wx_dir,
            'name': self.info['name'],
            'mobile': self.info['mobile']
        }
        try:
            if not os.path.exists('./app/data'):
                os.mkdir('./app/data')
            with open('./app/data/info.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(dic))
        except:
            with open('./info.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(dic))
        self.DecryptSignal.emit(True)
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
        try:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
        except:
            os.mkdir('app')
            os.mkdir('app/DataBase')
            os.mkdir('app/DataBase/Msg')
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
