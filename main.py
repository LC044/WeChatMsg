import ctypes
import sys
import time
import traceback

from app.ui.Icon import Icon

widget = None


def excepthook(exc_type, exc_value, traceback_):
    # 将异常信息转为字符串

    # 在这里处理全局异常

    error_message = ''.join(traceback.format_exception(exc_type, exc_value, traceback_))
    txt = '您可添加QQ群发送log文件以便解决该问题'
    msg = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\ndetails: {error_message}\n\n{txt}"
    logger.error(f'程序发生了错误:\n\n{msg}')
    # 创建一个 QMessageBox 对象
    error_box = QMessageBox()

    # 设置对话框的标题
    error_box.setWindowTitle("未知错误")
    pixmap = QPixmap(Icon.logo_ico_path)
    icon = QIcon(pixmap)
    error_box.setWindowIcon(icon)
    # 设置对话框的文本消息
    error_box.setText(msg)
    # 设置对话框的图标，使用 QMessageBox.Critical 作为图标类型
    error_box.setIcon(QMessageBox.Critical)
    # 添加一个“确定”按钮
    error_box.addButton(QMessageBox.Ok)
    # 显示对话框
    error_box.exec_()

    # 调用原始的 excepthook，以便程序正常退出
    sys.__excepthook__(exc_type, exc_value, traceback_)


# 设置 excepthook
sys.excepthook = excepthook
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from app.DataBase import close_db
from app.log import logger
from app.ui import mainview
from app.ui.tool.pc_decrypt import pc_decrypt
from app.config import version

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


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
            self.viewMainWindow.init_ui()
            print('ok', '本次加载用了', end - start, 's')

        except Exception as e:
            print(f"Exception: {e}")
            logger.error(traceback.format_exc())

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
    widget = view.viewMainWindow
    try:
        # view.loadPCDecryptView()
        view.loadMainWinView()
        # view.show()
        # view.show_success()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Exception: {e}")
        logger.error(traceback.format_exc())
