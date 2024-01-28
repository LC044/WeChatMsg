from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel

from app.ui.Icon import Icon
from .pc_decrypt import DecryptControl
from .setting.setting import SettingControl
from .get_bias_addr.get_bias_addr import GetBiasAddrControl
from .toolUI import Ui_Dialog

# 美化样式表
Stylesheet = """
QPushButton{
    background-color: rgb(250,252,253);
    border-radius: 5px;
    padding: 8px;
    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
}
QPushButton:hover { 
    background-color: lightgray;
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 400px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
    color: black;
    border:none;
}
QListWidget::item{
    min-width: 80px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    border-left:none;
    color: black;
    font-weight: bold;
}

"""


class ToolWindow(QWidget, Ui_Dialog):
    get_info_signal = pyqtSignal(str)
    decrypt_success_signal = pyqtSignal(bool)
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setStyleSheet(Stylesheet)
        self.init_ui()
        self.load_finish_signal.emit(True)

    def init_ui(self):
        self.listWidget.clear()
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        chat_item = QListWidgetItem(Icon.Decrypt_Icon, '解密', self.listWidget)
        contact_item = QListWidgetItem(Icon.Contact_Icon, '设置', self.listWidget)
        myinfo_item = QListWidgetItem(Icon.Home_Icon, '解密2', self.listWidget)
        tool_item = QListWidgetItem(Icon.Home_Icon, '别点', self.listWidget)

        self.decrypt_window = DecryptControl()
        self.decrypt_window.get_wxidSignal.connect(self.get_info_signal)
        self.decrypt_window.DecryptSignal.connect(self.decrypt_success_signal)
        self.decrypt_window.versionErrorSignal.connect(self.show_decrypt2)
        self.stackedWidget.addWidget(self.decrypt_window)

        setting_window = SettingControl()
        self.stackedWidget.addWidget(setting_window)

        self.get_bias_addr_window = GetBiasAddrControl()
        self.get_bias_addr_window.biasAddrSignal.connect(self.decrypt)
        self.stackedWidget.addWidget(self.get_bias_addr_window)

        label = QLabel('都说了不让你点', self)
        label.setFont(QFont("微软雅黑", 50))
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        # label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
        #     randint(0, 255), randint(0, 255), randint(0, 255)))

        self.stackedWidget.addWidget(label)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)

    def decrypt(self, version_list):
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)
        self.decrypt_window.version_list = version_list
        self.decrypt_window.get_info()

    def show_decrypt2(self, version):
        self.listWidget.setCurrentRow(2)
        self.stackedWidget.setCurrentIndex(2)

    def setCurrentIndex(self, row):
        self.stackedWidget.setCurrentIndex(row)
