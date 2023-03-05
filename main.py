from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from app.Ui import *


#
class ViewController:
    def loadDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = decrypt.DecryptControl()  # 需要将viewlogin设为成员变量
        self.viewDecrypt.DecryptSignal.connect(self.loadMainWinView)
        self.viewDecrypt.registerSignal.connect(self.loadRegisterView)
        self.viewDecrypt.show()
        self.viewDecrypt.db_exist()

    def loadRegisterView(self):
        """
        注册界面
        :return:
        """
        self.viewDecrypt = register.registerControl()  # 需要将viewlogin设为成员变量
        self.viewDecrypt.DecryptSignal.connect(self.loadDecryptView)
        self.viewDecrypt.show()

    def loadMainWinView(self, username):
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
    # view.loadDecryptView()  # 进入登录界面，如果viewlogin不是成员变量，则离开作用域后失效。
    view.loadMainWinView('102')
    sys.exit(app.exec_())
