import ctypes
import sys
import time

from PyQt5.QtWidgets import *

import app.DataBase.data as DB
from app.Ui import decrypt, mainview, pc_decrypt

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController:
    def __init__(self):
        self.viewMainWIn = None
        self.viewDecrypt = None

    def loadDecryptView(self):
        """
        登录界面
        :return:
        """
        if DB.is_db_exist():
            self.loadMainWinView()
        else:
            self.viewDecrypt = decrypt.DecryptControl()  # 需要将view login设为成员变量
            self.viewDecrypt.DecryptSignal.connect(self.loadMainWinView)
            self.viewDecrypt.show()
            self.viewDecrypt.db_exist()

    def loadPCDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = pc_decrypt.DecryptControl()
        self.viewDecrypt.DecryptSignal.connect(self.loadMainWinView)
        self.viewDecrypt.show()

    def loadMainWinView(self, username=None):
        """
        聊天界面
        :param username: 账号
        :return:
        """
        username = ''
        start = time.time()
        self.viewMainWIn = mainview.MainWinController(username=username)
        self.viewMainWIn.setWindowTitle("Chat")
        # print(username)
        self.viewMainWIn.username = username
        # self.viewMainWIn.exitSignal.connect(self.loadDecryptView)  # 不需要回到登录界面可以省略
        self.viewMainWIn.show()
        end = time.time()
        print('ok', end - start)
        # self.viewMainWIn.signUp()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    # view.loadPCDecryptView()
    view.loadDecryptView()  # 进入登录界面，如果view login不是成员变量，则离开作用域后失效。
    # view.loadMainWinView('102')
    sys.exit(app.exec_())
