import ctypes
import sys
import time
import traceback

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from app.DataBase import close_db
from app.log import logger
from app.ui import mainview
from app.ui.tool.pc_decrypt import pc_decrypt
from app.config import version
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController(QWidget):
    def __init__(self):
        super().__init__()
        self.viewMainWindow = None
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
        self.viewMainWindow = mainview.MainWinController(username=username)
        self.viewMainWindow.exitSignal.connect(self.close)
        try:
            self.viewMainWindow.setWindowTitle(f"留痕-{version}")
            self.viewMainWindow.show()
            end = time.time()
            print('ok', '本次加载用了', end - start, 's')
            self.viewMainWindow.init_ui()
        except Exception as e:
            print(f"Exception: {e}")
            logger.error(traceback.print_exc())

    def show_success(self):
        QMessageBox.about(self, "解密成功", "数据库文件存储在\napp/DataBase/Msg\n文件夹下")

    def close(self) -> bool:
        close_db()
        super().close()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont('微软雅黑', 12)  # 使用 Times New Roman 字体，字体大小为 14
    app.setFont(font)
    view = ViewController()
    try:
        # view.loadPCDecryptView()
        view.loadMainWinView()
        # view.show()
        # view.show_success()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Exception: {e}")
        logger.error(traceback.print_exc())
