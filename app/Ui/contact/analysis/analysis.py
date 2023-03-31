import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *

from . import charts


class AnalysisController(QWidget):
    def __init__(self, username):
        super().__init__()
        self.ta_username = username
        self.setWindowTitle('数据分析')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setStyleSheet('''QWidget{background-color:rgb(255, 255, 255);}''')
        # self.setBackground()
        self.resize(400, 300)
        self.center()
        self.setAttribute(Qt.WA_AttributeCount)
        self.label_01()
        self.Thread = LoadData(username)
        self.Thread.okSignal.connect(self.initUI)
        self.Thread.start()

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

    def label_01(self):
        self.label = QLabel(self)
        self.label.setGeometry(150, 100, 100, 100)
        self.label.setToolTip("这是一个标签")
        self.m_movie()

    def m_movie(self):
        movie = QMovie("./app/data/bg.gif")
        self.label.setMovie(movie)
        movie.start()

    def initUI(self):
        self.label.setVisible(False)
        main_box = QHBoxLayout(self)
        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('file:///data/聊天统计/title.html'))
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
        self.browser3.load(QUrl('file:///data/聊天统计/time.html'))
        self.browser4 = QWebEngineView()
        self.browser4.load(QUrl('http://www.baidu.com'))
        self.browser5 = QWebEngineView()
        self.browser5.load(QUrl('file:///data/聊天统计/chat_session.html'))
        self.browser6 = QWebEngineView()
        self.browser6.load(QUrl('file:///data/聊天统计/sports.html'))
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
        splitter1.setSizes([1, 8])

        splitter2.addWidget(splitter6)
        splitter2.addWidget(splitter3)
        splitter2.setSizes([1, 3])

        splitter3.addWidget(splitter4)
        splitter3.addWidget(splitter8)
        splitter3.setSizes([2, 1])

        splitter4.addWidget(splitter5)
        splitter4.addWidget(self.browser2)
        splitter4.setSizes([1, 5])

        splitter5.addWidget(self.browser3)
        # splitter5.addWidget(self.browser4)

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

    def setBackground(self):
        palette = QPalette()
        pix = QPixmap("./app/data/bg.png")
        pix = pix.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # 自适应图片大小
        palette.setBrush(self.backgroundRole(), QBrush(pix))  # 设置背景图片
        # palette.setColor(self.backgroundRole(), QColor(192, 253, 123))  # 设置背景颜色
        self.setPalette(palette)


class LoadData(QThread):
    """
    发送信息线程
    """
    okSignal = pyqtSignal(int)

    def __init__(self, ta_u, parent=None):
        super().__init__(parent)
        self.ta_username = ta_u

    def run(self):
        charts.chat_start_endTime(self.ta_username)
        charts.title(self.ta_username)
        charts.send_recv_rate(self.ta_username)
        charts.message_word_cloud(self.ta_username)
        charts.msg_type_rate(self.ta_username)
        charts.calendar_chart(self.ta_username)
        charts.month_num(self.ta_username)
        charts.sport(self.ta_username)
        charts.chat_session(self.ta_username)
        self.okSignal.emit(10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
