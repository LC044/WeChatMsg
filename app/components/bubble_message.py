from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QSpacerItem
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QRectF, QPoint


class TextMessage(QLabel):
    heightSingal = pyqtSignal(int)

    def __init__(self, text, is_send=False, parent=None):
        super(TextMessage, self).__init__(text, parent)
        self.setFont(QFont('SimSun', 15))
        self.setWordWrap(True)
        # self.adjustSize()
        self.setMaximumWidth(800)
        self.setMinimumWidth(100)
        self.setMinimumHeight(10)
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
        if self.Type == 3:
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


class Avatar(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar).scaled(45, 45))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar)
        self.setMaximumWidth(45)
        self.setMaximumHeight(45)


class ImageMessage(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        self.image_path = './Data/head.jpg'
        self.image = QLabel(self)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar)
        self.setMaximumWidth(480)
        self.setMaximumHeight(720)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.setScaledContents(True)

    # def paintEvent(self, a0) -> None:
    #     painter = QPainter(self)
    #     painter.begin(self)
    #     # self.setPixmap()
    #     painter.end()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 左键按下
            image = Image.open(self.image_path)
            image.show()


class BubbleMessage(QWidget):
    def __init__(self, str_content, avatar, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.isSend = is_send
        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.avatar = Avatar(avatar)
        triangle = Triangle(Type,is_send)
        if Type == 3:
            self.message = TextMessage(str_content, is_send)
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
        self.spacerItem = QSpacerItem(65, 65, QSizePolicy.Expanding, QSizePolicy.Minimum)
        if is_send:
            layout.addItem(self.spacerItem)
            layout.addWidget(self.message, 10)
            layout.addWidget(triangle,0,Qt.AlignTop | Qt.AlignLeft)
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignLeft)
            layout.setStretch(0, 1)
        else:
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(triangle, 0, Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(self.message, 10)
            layout.addItem(self.spacerItem)
            layout.setStretch(3, 1)
        self.setLayout(layout)


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        txt = '''在工具中单击边缘可以添加黑点，单击可以删掉黑点，拖动可以调整黑点长度。勾选等选项可以查看内容、缩放等区域右侧可预览不同拉伸情况下的效果，拖动可以调整预览的拉伸比例'''
        avatar = 'Data/head.jpg'
        bubble_message = BubbleMessage(txt, avatar, Type=3, is_send=False)
        layout = QVBoxLayout()
        txt = "你说啥"
        avatar_2 = 'Data/fg1.png'
        bubble_message1 = BubbleMessage(txt, avatar_2, Type=3, is_send=True)
        layout.addWidget(bubble_message)
        layout.addWidget(bubble_message1)
        bubble_message2 = BubbleMessage('', avatar_2, Type=3, is_send=True)
        layout.addWidget(bubble_message2)
        txt = "我啥都没说"
        avatar0 = 'Data/fg1.png'
        bubble_message1 = BubbleMessage('Data/fg1.png', avatar, Type=1, is_send=False)
        layout.addWidget(bubble_message1)
        self.spacerItem = QSpacerItem(65, 65, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(self.spacerItem)
        # layout.setStretch(0, 1)
        self.setLayout(layout)

    # def resizeEvent(self, a0) -> None:
    #     return


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
