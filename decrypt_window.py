import ctypes
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

from app.resources import resource_rc
from app.ui_pc.tool.pc_decrypt import pc_decrypt

var = resource_rc.qt_resource_name
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('解密')
        self.setWindowIcon(QIcon(':/icons/icons/logo.svg'))
        self.viewMainWIn = None
        self.viewDecrypt = None

    def loadPCDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = pc_decrypt.DecryptControl(self)
        self.viewDecrypt.DecryptSignal.connect(self.show_success)
        # self.viewDecrypt.show()

    def show_success(self):
        QMessageBox.about(self, "解密成功", "数据库文件存储在\napp/DataBase/Msg\n文件夹下")
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    view.loadPCDecryptView()
    view.show()
    sys.exit(app.exec_())
