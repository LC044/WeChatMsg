from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from app.DataBase import data

# class AnalysisController(QMainWindow, Ui_Dialog):
#     exitSignal = pyqtSignal()
#
#     # username = ''
#     def __init__(self, username, parent=None):
#         super(AnalysisController, self).__init__(parent)
#         self.setupUi(self)
#         self.setWindowTitle('WeChat')
#         self.setWindowIcon(QIcon('./app/data/icon.png'))
#         self.Me = data.get_myinfo()
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QSplitter, QApplication)
from PyQt5.QtCore import (Qt, QUrl)
from PyQt5.QtWebEngineWidgets import *
from . import charts


class AnalysisController(QWidget):
    def __init__(self, username):
        super().__init__()
        self.ta_username = username
        self.load_data()
        self.initUI()
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        # self.setBackground()

    def load_data(self):
        charts.send_recv_rate(self.ta_username)
        charts.message_word_cloud(self.ta_username)
        charts.msg_type_rate(self.ta_username)
        charts.calendar_chart(self.ta_username)
        charts.month_num(self.ta_username)

    def initUI(self):
        main_box = QHBoxLayout(self)
        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('http://www.baidu.com'))
        # self.browser1 = QFrame(self)
        # self.browser1.setFrameShape(QFrame.StyledPanel)
        # self.layoutWidget = QtWidgets.QWidget(self.browser1)
        # # self.layoutWidget.setGeometry(QtCore.QRect(71, 63, 227, 155))
        # self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        # self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        # _translate = QtCore.QCoreApplication.translate
        # conRemark = data.get_conRemark(self.ta_username)
        # self.label_2.setText(_translate("Dialog", f"{conRemark}"))
        # self.horizontalLayout_2.addWidget(self.label_2)
        # self.browser1.setLayout(self.horizontalLayout_2)

        self.browser2 = QWebEngineView()
        self.browser2.load(QUrl('file:///data/聊天统计/wordcloud.html'))
        self.browser3 = QWebEngineView()
        self.browser3.load(QUrl('http://www.baidu.com'))
        self.browser4 = QWebEngineView()
        self.browser4.load(QUrl('http://www.baidu.com'))
        self.browser5 = QWebEngineView()
        self.browser5.load(QUrl('http://www.baidu.com'))
        self.browser6 = QWebEngineView()
        self.browser6.load(QUrl('http://www.baidu.com'))
        self.browser7 = QWebEngineView()
        self.browser7.load(QUrl('file:///data/聊天统计/month_num.html'))
        self.browser8 = QWebEngineView()
        self.browser8.load(QUrl('file:///data/聊天统计/calendar.html'))
        self.browser9 = QWebEngineView()
        self.browser9.load(QUrl('file:///data/聊天统计/msg_type_rate.html'))
        self.browser10 = QWebEngineView()
        self.browser10.load(QUrl('file:///data/聊天统计/send_recv_rate.html'))

        splitter1 = QSplitter(Qt.Vertical)
        splitter2 = QSplitter(Qt.Horizontal)
        splitter3 = QSplitter(Qt.Horizontal)
        splitter4 = QSplitter(Qt.Vertical)
        splitter5 = QSplitter(Qt.Horizontal)
        splitter6 = QSplitter(Qt.Vertical)
        splitter7 = QSplitter(Qt.Vertical)
        splitter8 = QSplitter(Qt.Vertical)
        splitter9 = QSplitter(Qt.Vertical)

        splitter1.addWidget(self.browser1)
        splitter1.addWidget(splitter2)
        splitter1.setSizes([1, 5])

        splitter2.addWidget(splitter6)
        splitter2.addWidget(splitter3)
        splitter2.setSizes([1, 3])

        splitter3.addWidget(splitter4)
        splitter3.addWidget(splitter8)
        splitter3.setSizes([2, 1])

        splitter4.addWidget(splitter5)
        splitter4.addWidget(self.browser2)
        splitter4.setSizes([1, 3])

        splitter5.addWidget(self.browser3)
        splitter5.addWidget(self.browser4)

        splitter6.addWidget(self.browser5)
        splitter6.addWidget(splitter7)
        splitter6.setSizes([1, 2])

        splitter7.addWidget(self.browser6)
        splitter7.addWidget(self.browser7)

        splitter8.addWidget(self.browser8)
        splitter8.addWidget(splitter9)
        splitter8.setSizes([1, 2])

        splitter9.addWidget(self.browser9)
        splitter9.addWidget(self.browser10)

        main_box.addWidget(splitter1)
        self.setLayout(main_box)
        self.setGeometry(300, 300, 600, 500)

    def setBackground(self):
        palette = QPalette()
        pix = QPixmap("./app/data/bg.png")
        pix = pix.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # 自适应图片大小
        palette.setBrush(self.backgroundRole(), QBrush(pix))  # 设置背景图片
        # palette.setColor(self.backgroundRole(), QColor(192, 253, 123))  # 设置背景颜色
        self.setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
