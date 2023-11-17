from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QSpacerItem, \
    QScrollArea, QScrollBar


class TextMessage(QLabel):
    heightSingal = pyqtSignal(int)

    def __init__(self, text, is_send=False, parent=None):
        super(TextMessage, self).__init__(text, parent)
        self.setFont(QFont('微软雅黑', 12))
        self.setWordWrap(True)
        # self.adjustSize()
        self.setMaximumWidth(800)
        self.setMinimumWidth(100)
        self.setMinimumHeight(45)
        # self.resize(QSize(100,40))

        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        if is_send:
            self.setAlignment(Qt.AlignCenter | Qt.AlignRight)
            self.setStyleSheet(
                '''
                background-color:white;
                border-radius:10px;
                border-top: 10px solid white;
                border-bottom: 10px solid white;
                border-right: 10px solid white;
                border-left: 10px solid white;
                '''
            )
        else:
            self.setStyleSheet(
                '''
                background-color:#b2e281;
                border-radius:10px;
                border-top: 10px solid #b2e281;
                border-bottom: 10px solid #b2e281;
                border-right: 10px solid #b2e281;
                border-left: 10px solid #b2e281;
                '''
            )
        w = len(text) * 16 + 30
        if w < self.width():
            self.setMaximumWidth(w)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(TextMessage, self).paintEvent(a0)


class Triangle(QLabel):
    def __init__(self, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.Type = Type
        self.is_send = is_send
        self.setFixedSize(6, 45)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(Triangle, self).paintEvent(a0)
        if self.Type == 1:
            painter = QPainter(self)
            triangle = QPolygon()
            # print(self.width(), self.height())
            if self.is_send:
                painter.setPen(QColor('white'))
                painter.setBrush(QColor('white'))
                triangle.setPoints(0, 20, 0, 35, 6, 25)
            else:
                painter.setPen(QColor('#b2e281'))
                painter.setBrush(QColor('#b2e281'))
                triangle.setPoints(0, 25, 6, 20, 6, 35)
            painter.drawPolygon(triangle)


class Notice(QLabel):
    def __init__(self, text, type_=3, parent=None):
        super().__init__(text, parent)
        self.type_ = type_
        self.setFont(QFont('微软雅黑', 12))
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setAlignment(Qt.AlignCenter)


class Avatar(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar).scaled(45, 45))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar.scaled(45, 45))
        self.setFixedSize(QSize(45, 45))


class OpenImageThread(QThread):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self) -> None:
        image = Image.open(self.image_path)
        image.show()


class ImageMessage(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        self.image = QLabel(self)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar)
        self.setMaximumWidth(480)
        self.setMaximumHeight(720)
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 左键按下
            self.open_image_thread = OpenImageThread(self.image_path)
            self.open_image_thread.start()


class BubbleMessage(QWidget):
    def __init__(self, str_content, avatar, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.isSend = is_send
        # self.set
        self.setStyleSheet(
            '''
            border:none;
            '''
        )
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 5, 5, 5)
        self.avatar = Avatar(avatar)
        triangle = Triangle(Type, is_send)
        if Type == 1:
            self.message = TextMessage(str_content, is_send)
            # self.message.setMaximumWidth(int(self.width() * 0.6))
        else:
            self.message = ImageMessage(str_content)
        # skin_aio_friend_bubble_pressed.9
        '''
        border-image:url(./Data/截图222.png) 20 20 20 20;
        border-top: 5px transparent;
        border-bottom: 5px transparent;
        border-right: 5px transparent;
        border-left: 5px transparent;
        border-radius:10px;
        '''
        self.spacerItem = QSpacerItem(45 + 6, 45, QSizePolicy.Expanding, QSizePolicy.Minimum)
        if is_send:
            layout.addItem(self.spacerItem)
            layout.addWidget(self.message, 1)
            layout.addWidget(triangle, 0, Qt.AlignTop | Qt.AlignLeft)
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignLeft)
        else:
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(triangle, 0, Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(self.message, 1)
            layout.addItem(self.spacerItem)
        self.setLayout(layout)


class ScrollAreaContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setStyleSheet(
        #     '''
        #     background-color:rgb(127,127,127);
        #     '''
        # )

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # print(self.width(),self.height())
        self.setMinimumSize(self.width(), self.height())


class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet(
            '''
            border:none;
            '''
        )

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # return
        self.widget().setMinimumSize(self.width(), self.widget().height())
        self.widget().setMaximumSize(self.width(), self.widget().height())
        self.widget().resize(QSize(self.width(), self.widget().height()))


#

class ScrollBar(QScrollBar):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            '''
          QScrollBar:vertical {
              border-width: 0px;
              border: none;
              background:rgba(64, 65, 79, 0);
              width:5px;
              margin: 0px 0px 0px 0px;
          }
          QScrollBar::handle:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 #DDDDDD, stop: 0.5 #DDDDDD, stop:1 #aaaaff);
              min-height: 20px;
              max-height: 20px;
              margin: 0 0px 0 0px;
              border-radius: 2px;
          }
          QScrollBar::add-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 rgba(64, 65, 79, 0), stop: 0.5 rgba(64, 65, 79, 0),  stop:1 rgba(64, 65, 79, 0));
              height: 0px;
              border: none;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0  rgba(64, 65, 79, 0), stop: 0.5 rgba(64, 65, 79, 0),  stop:1 rgba(64, 65, 79, 0));
              height: 0 px;
              border: none;
              subcontrol-position: top;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-page:vertical {
              background: rgba(64, 65, 79, 0);
          }

          QScrollBar::add-page:vertical {
              background: rgba(64, 65, 79, 0);
          }
            '''
        )


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        txt = '''在工具中单击边缘可以添加黑点，单击可以删掉黑点，拖动可以调整黑点长度。勾选等选项可以查看内容、缩放等区域右侧可预览不同拉伸情况下的效果，拖动可以调整预览的拉伸比例'''
        avatar = '../data/icons/default_avatar.svg'
        bubble_message = BubbleMessage(txt, avatar, Type=1, is_send=False)
        layout = QVBoxLayout()
        layout.setSpacing(0)

        # 生成滚动区域
        self.scrollArea = ScrollArea()
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)
        # self.scrollArea.setGeometry(QRect(9, 9, 261, 211))
        # 生成滚动区域的内容部署层部件
        self.scrollAreaWidgetContents = ScrollAreaContent()
        self.scrollAreaWidgetContents.setMinimumSize(50, 100)
        # 设置滚动区域的内容部署部件为前面生成的内容部署层部件
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea)
        layout0 = QVBoxLayout()
        layout0.setSpacing(0)
        # self.scrollArea.setLayout(layout0)
        self.scrollAreaWidgetContents.setLayout(layout0)

        time = Notice("2023-11-17 15:44")
        layout0.addWidget(time)
        txt = "你说啥"
        avatar_2 = '../data/icons/default_avatar.svg'
        bubble_message1 = BubbleMessage(txt, avatar_2, Type=1, is_send=True)
        layout0.addWidget(bubble_message)
        layout0.addWidget(bubble_message1)

        bubble_message2 = BubbleMessage('', avatar_2, Type=1, is_send=True)
        layout0.addWidget(bubble_message2)
        txt = "我啥都没说"
        avatar0 = 'Data/fg1.png'
        bubble_message1 = BubbleMessage("D:\Project\Python\PyQt-master\QLabel\Data\\fg1.png", avatar, Type=3,
                                        is_send=False)
        layout0.addWidget(bubble_message1)

        self.spacerItem = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout0.addItem(self.spacerItem)
        # layout.setStretch(0, 1)
        self.setLayout(layout)


class Test(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.resize(500, 600)
        w1 = MyWidget()
        w2 = QLabel("nihao")
        layout.addWidget(w1)
        layout.addWidget(w2)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    widget = Test()
    # widget = MyWidget()
    widget.show()
    app.exec_()
