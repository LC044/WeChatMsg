import ctypes
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from app.Ui import pc_decrypt

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('解密')
        self.setWindowIcon(QIcon('./app/data/icons/logo.svg'))
        self.viewMainWIn = None
        self.viewDecrypt = None

    def loadPCDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = pc_decrypt.DecryptControl()
        self.viewDecrypt.DecryptSignal.connect(self.show_success)
        self.viewDecrypt.show()

    def show_success(self):
        QMessageBox.about(self, "解密成功", "数据库文件存储在\napp/DataBase/Msg\n文件夹下")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    view.loadPCDecryptView()
    # view.show_success()
    sys.exit(app.exec_())
