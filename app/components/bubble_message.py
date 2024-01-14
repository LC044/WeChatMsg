import os.path
import subprocess
import platform

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QPolygon, QFontMetrics
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QSpacerItem, \
    QScrollArea

from app.components.scroll_bar import ScrollBar


class MessageType:
    Text = 1
    Image = 3


class TextMessage(QLabel):
    heightSingal = pyqtSignal(int)

    def __init__(self, text, is_send=False, parent=None):
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        super(TextMessage, self).__init__(text, parent)
        font = QFont('微软雅黑', 12)
        self.setFont(font)
        self.setWordWrap(True)
        self.setMaximumWidth(800)
        # self.setMinimumWidth(100)
        self.setMinimumHeight(45)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if is_send:
            self.setAlignment(Qt.AlignCenter | Qt.AlignRight)
            self.setStyleSheet(
                '''
                background-color:#b2e281;
                border-radius:10px;
                padding:10px;
                '''
            )
        else:
            self.setStyleSheet(
                '''
                background-color:white;
                border-radius:10px;
                padding:10px;
                '''
            )
        font_metrics = QFontMetrics(font)
        rect = font_metrics.boundingRect(text)
        # rect = font_metrics
        self.setMaximumWidth(rect.width() + 40)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(TextMessage, self).paintEvent(a0)


class Triangle(QLabel):
    def __init__(self, Type, is_send=False, position=(0, 0), parent=None):
        """

        @param Type:
        @param is_send:
        @param position:(x,y)
        @param parent:
        """
        super().__init__(parent)
        self.Type = Type
        self.is_send = is_send
        self.position = position

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        super(Triangle, self).paintEvent(a0)
        if self.Type == MessageType.Text:
            self.setFixedSize(6, 45)
            painter = QPainter(self)
            triangle = QPolygon()
            x, y = self.position
            if self.is_send:
                painter.setPen(QColor('#b2e281'))
                painter.setBrush(QColor('#b2e281'))
                triangle.setPoints(0, 20+y, 0, 34+y, 6, 27+y)
            else:
                painter.setPen(QColor('white'))
                painter.setBrush(QColor('white'))
                triangle.setPoints(0, 27+y, 6, 20+y, 6, 34+y)
            painter.drawPolygon(triangle)


class Notice(QLabel):
    def __init__(self, text, type_=3, parent=None):
        super().__init__(text, parent)
        self.type_ = type_
        self.setFont(QFont('微软雅黑', 10))
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


def open_image_viewer(file_path):
    system_platform = platform.system()

    if system_platform == "Darwin":  # macOS
        subprocess.run(["open", file_path])
    elif system_platform == "Windows":
        subprocess.run(["start", " ", file_path], shell=True)
    elif system_platform == "Linux":
        subprocess.run(["xdg-open", file_path])
    else:
        print("Unsupported platform")


class OpenImageThread(QThread):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self) -> None:
        if os.path.exists(self.image_path):
            open_image_viewer(self.image_path)


class ImageMessage(QLabel):
    def __init__(self, image, is_send, image_link='', max_width=480, max_height=240, parent=None):
        """
        param:image 图像路径或者QPixmap对象
        param:image_link='' 点击图像打开的文件路径
        """
        super().__init__(parent)
        self.image = QLabel(self)
        self.max_width = max_width
        self.max_height = max_height
        # self.setFixedSize(self.max_width,self.max_height)
        self.setMaximumWidth(self.max_width)
        self.setMaximumHeight(self.max_height)
        self.setCursor(Qt.PointingHandCursor)
        if isinstance(image, str):
            pixmap = QPixmap(image)
            self.image_path = image
        elif isinstance(image, QPixmap):
            pixmap = image
        self.set_image(pixmap)
        if image_link:
            self.image_path = image_link
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if is_send:
            self.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        # self.setScaledContents(True)

    def set_image(self, pixmap):
        # 计算调整后的大小
        adjusted_width = min(pixmap.width(), self.max_width)
        adjusted_height = min(pixmap.height(), self.max_height)
        self.setPixmap(pixmap.scaled(adjusted_width, adjusted_height, Qt.KeepAspectRatio))
        # 调整QLabel的大小以适应图片的宽高，但不超过最大宽高
        # self.setFixedSize(adjusted_width, adjusted_height)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 左键按下
            print('打开图像', self.image_path)
            self.open_image_thread = OpenImageThread(self.image_path)
            self.open_image_thread.start()


class BubbleMessage(QWidget):
    def __init__(self, str_content, avatar, Type, is_send=False, display_name=None, parent=None):
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
        # self.resize(QSize(200, 50))
        self.avatar = Avatar(avatar)
        triangle = Triangle(Type, is_send, (0, 0))
        if Type == MessageType.Text:
            self.message = TextMessage(str_content, is_send)
            # self.message.setMaximumWidth(int(self.width() * 0.6))
        elif Type == MessageType.Image:
            self.message = ImageMessage(str_content, is_send)
        else:
            raise ValueError("未知的消息类型")
        if display_name:
            triangle = Triangle(Type, is_send, (0, 10))
            label_name = QLabel(display_name, self)
            label_name.setFont(QFont('微软雅黑', 10))
            if is_send:
                label_name.setAlignment(Qt.AlignRight)
            vlayout = QVBoxLayout()
            vlayout.setSpacing(0)
            if is_send:
                vlayout.addWidget(label_name, 0, Qt.AlignTop | Qt.AlignRight)
                vlayout.addWidget(self.message, 0, Qt.AlignTop | Qt.AlignRight)
            else:
                vlayout.addWidget(label_name)
                vlayout.addWidget(self.message)
        self.spacerItem = QSpacerItem(45 + 6, 45, QSizePolicy.Expanding, QSizePolicy.Minimum)
        if is_send:
            layout.addItem(self.spacerItem)
            if display_name:
                layout.addLayout(vlayout, 1)
            else:
                layout.addWidget(self.message, 1)
            layout.addWidget(triangle, 0, Qt.AlignTop | Qt.AlignLeft)
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignLeft)
        else:
            layout.addWidget(self.avatar, 0, Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(triangle, 0, Qt.AlignTop | Qt.AlignRight)
            if display_name:
                layout.addLayout(vlayout, 1)
            else:
                layout.addWidget(self.message, 1)
            layout.addItem(self.spacerItem)
        self.setLayout(layout)


class ScrollAreaContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.adjustSize()


class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            '''
            border:none;
            '''
        )


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.adjustSize()
        # 生成滚动区域
        self.scrollArea = ScrollArea(self)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)
        # 生成滚动区域的内容部署层部件
        self.scrollAreaWidgetContents = ScrollAreaContent(self.scrollArea)
        self.scrollAreaWidgetContents.setMinimumSize(50, 100)
        # 设置滚动区域的内容部署部件为前面生成的内容部署层部件
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea)
        self.layout0 = QVBoxLayout()
        self.layout0.setSpacing(0)
        self.scrollAreaWidgetContents.setLayout(self.layout0)
        self.setLayout(layout)

    def add_message_item(self, bubble_message, index=1):
        if index:
            self.layout0.addWidget(bubble_message)
        else:
            self.layout0.insertWidget(0, bubble_message)
        # self.set_scroll_bar_last()

    def set_scroll_bar_last(self):
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )

    def set_scroll_bar_value(self, val):
        self.verticalScrollBar().setValue(val)

    def verticalScrollBar(self):
        return self.scrollArea.verticalScrollBar()

    def update(self) -> None:
        super().update()
        self.scrollAreaWidgetContents.adjustSize()
        self.scrollArea.update()
        # self.scrollArea.repaint()
        # self.verticalScrollBar().setMaximum(self.scrollAreaWidgetContents.height())
