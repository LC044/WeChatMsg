from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog

try:
    from .dialog import Ui_Dialog
    from app import config
    from app.resources import resource_rc
except:
    from dialog import Ui_Dialog
    from ..resources import resource_rc


class AboutDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('关于')
        self.resize(QSize(640,520))
        self.init_ui()

    def init_ui(self):
        pixmap = QPixmap(':/icons/icons/logo99.png')
        self.label_logo.setPixmap(pixmap)
        pixmap = QPixmap(':/icons/icons/weixin.png')
        self.label_weixin.setPixmap(pixmap)
        self.label_version.setText('《留痕》')
        self.textBrowser.setHtml(config.about)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = AboutDialog()
    result = dialog.exec_()  # 使用exec_()获取用户的操作结果
    if result == QDialog.Accepted:
        print("用户点击了导出按钮")
    else:
        print("用户点击了取消按钮")
    sys.exit(app.exec_())
