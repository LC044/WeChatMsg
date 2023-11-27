import ctypes
import sys
import time

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from app.ui_pc import mainview
from app.ui_pc.tool.pc_decrypt import pc_decrypt

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('解密')
        self.setWindowIcon(QIcon(':/icons/icons/logo.png'))
        self.viewMainWIndow = None
        self.viewDecrypt = None

    def loadPCDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = pc_decrypt.DecryptControl()
        self.viewDecrypt.DecryptSignal.connect(self.show_success)
        self.viewDecrypt.show()

    def loadMainWinView(self, username=None):
        """
        聊天界面
        :param username: 账号
        :return:
        """
        username = ''
        start = time.time()
        self.viewMainWIndow = mainview.MainWinController(username=username)
        self.viewMainWIndow.setWindowTitle("Chat")
        # print(username)
        self.viewMainWIndow.username = username
        # self.viewMainWIn.exitSignal.connect(self.loadDecryptView)  # 不需要回到登录界面可以省略

        self.viewMainWIndow.show()
        end = time.time()
        print('ok', end - start)
        self.viewMainWIndow.init_ui()

    def show_success(self):
        QMessageBox.about(self, "解密成功", "数据库文件存储在\napp/DataBase/Msg\n文件夹下")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    # view.loadPCDecryptView()
    view.loadMainWinView()
    # view.show()
    # view.show_success()
    sys.exit(app.exec_())
