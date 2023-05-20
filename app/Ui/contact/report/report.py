import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *


class ReportController(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.ta_username = username

        # self.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')
        # 加载动画
        self.center()
        self.label_01()

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

    def label_01(self):
        w = self.size().width()
        h = self.size().height()
        self.label = QLabel(self)
        self.label.setGeometry(w // 2, h // 2, 100, 100)
        self.label.setToolTip("这是一个标签")
        # self.m_movie()
        self.initUI()

    def m_movie(self):
        movie = QMovie("./app/data/bg.gif")
        self.label.setMovie(movie)
        movie.start()

    def initUI(self):
        self.label.setVisible(False)
        # self.setStyleSheet('''QWidget{background-color:rgb(244, 244, 244);}''')
        main_box = QHBoxLayout(self)
        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('file:///data/AnnualReport/index.html'))
        # self.browser1.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')

        splitter1 = QSplitter(Qt.Vertical)

        splitter1.addWidget(self.browser1)
        main_box.addWidget(splitter1)
        self.setLayout(main_box)

    def setBackground(self):
        palette = QPalette()
        pix = QPixmap("./app/data/bg.png")
        pix = pix.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # 自适应图片大小
        palette.setBrush(self.backgroundRole(), QBrush(pix))  # 设置背景图片
        # palette.setColor(self.backgroundRole(), QColor(192, 253, 123))  # 设置背景颜色
        self.setPalette(palette)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReportController(1)
    ex.show()
    sys.exit(app.exec_())
