# -*- coding: utf-8 -*-
"""
@File    : decrypt.py
@Author  : Shuaikang Zhou
@Time    : 2023/1/5 18:13
@IDE     : Pycharm
@Version : Python3.10
@comment : ··· 解密数据库，导出原始数据库文件
"""
import hashlib
import os
import time
import xml.etree.ElementTree as ET

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import decryptUi
from ...DataBase import data


class DecryptControl(QWidget, decryptUi.Ui_Dialog):
    DecryptSignal = pyqtSignal(str)
    registerSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DecryptControl, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('解密')
        self.setWindowIcon(QIcon('./app/data/icons/logo.svg'))
        self.btn_db.clicked.connect(self.get_db)
        self.btn_xml.clicked.connect(self.get_xml)
        self.pushButton_3.clicked.connect(self.decrypt)
        self.xml_path = None
        self.db_path = None

    def db_exist(self):
        if os.path.exists('./app/DataBase/Msg.db'):
            self.btnEnterClicked()
            self.close()

    def get_xml(self):
        self.xml_path, _ = QFileDialog.getOpenFileName(self, 'Open file', r'..', "Xml files (*.xml)")
        if self.xml_path:
            self.label_xml.setText('xml已就绪')
            key = self.parser_xml()
            self.label_key.setText(f'数据库密钥：{key}')
            return self.xml_path
        return False

    def get_db(self):
        self.db_path, _ = QFileDialog.getOpenFileName(self, 'Open file', r'..', "Database files (*.db)")
        if self.db_path:
            self.label_db.setText('数据库已就绪')
            return self.db_path
        return False

    def decrypt(self):
        if not (self.xml_path and self.db_path):
            QMessageBox.critical(self, "错误", "请把两个文件加载进来")
            return
        key = self.parser_xml()
        self.label_key.setText(f'数据库密钥：{key}')
        self.thread1 = MyThread()
        self.thread1.signal.connect(self.progressBar_view)
        self.thread1.start()
        self.thread2 = DecryptThread(self.db_path, key)
        self.thread2.signal.connect(self.progressBar_view)
        self.thread2.start()

    def parser_xml(self):
        if not self.xml_path:
            return False
        pid = self.pid(self.xml_path)
        if not pid:
            return False
        key = self.key(pid)
        return key

    def pid(self, xml_path):
        tree = ET.parse(xml_path)
        # 根节点
        root = tree.getroot()
        # 标签名
        for stu in root:
            if stu.attrib["name"] == '_auth_uin':
                return stu.attrib['value']
        return False

    def key(self, uin, IMEI='1234567890ABCDEF'):
        m = hashlib.md5()
        m.update(bytes((IMEI + uin).encode('utf-8')))
        psw = m.hexdigest()
        return psw[:7]

    def btnEnterClicked(self):
        # print("enter clicked")
        # 中间可以添加处理逻辑
        self.DecryptSignal.emit('ok')
        self.close()

    def progressBar_view(self, value):
        """
        进度条显示
        :param value: 进度0-100
        :return: None
        """
        self.progressBar.setProperty('value', value)
        if value == '100':
            QMessageBox.information(self, "解密成功", "请退出该界面",
                                    QMessageBox.Yes)
            self.btnExitClicked()
            data.init_database()

    def btnExitClicked(self):
        # print("Exit clicked")
        self.DecryptSignal.emit('ok')
        self.close()


class DecryptThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, db_path, key):
        super(DecryptThread, self).__init__()
        self.db_path = db_path
        self.key = key
        self.textBrowser = None

    def __del__(self):
        pass

    def run(self):
        data.decrypt(self.db_path, self.key)
        self.signal.emit('100')


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
