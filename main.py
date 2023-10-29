import sys

from PyQt5.QtWidgets import *

import app.DataBase.data as DB
from app.Ui import *


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
            self.viewDecrypt.registerSignal.connect(self.loadRegisterView)
            self.viewDecrypt.show()
            self.viewDecrypt.db_exist()

    def loadRegisterView(self):
        """
        注册界面
        :return:
        """
        pass
        # self.viewDecrypt = register.registerControl()  # 需要将view login设为成员变量
        # self.viewDecrypt.DecryptSignal.connect(self.loadDecryptView)
        # self.viewDecrypt.show()

    def loadMainWinView(self, username=None):
        """
        聊天界面
        :param username: 账号
        :return:
        """
        username = ''
        self.viewMainWIn = mainview.MainWinController(username=username)
        self.viewMainWIn.setWindowTitle("Chat")
        # print(username)
        self.viewMainWIn.username = username
        # self.viewMainWIn.exitSignal.connect(self.loadDecryptView)  # 不需要回到登录界面可以省略
        self.viewMainWIn.show()
        # self.viewMainWIn.signUp()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    view.loadDecryptView()  # 进入登录界面，如果view login不是成员变量，则离开作用域后失效。
    # view.loadMainWinView('102')
    sys.exit(app.exec_())
