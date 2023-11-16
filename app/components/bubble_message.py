import sys

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from Lib import QtNinePatch2


class Label(QLabel):

    def __init__(self, *args, **kwargs):
        super(Label, self).__init__()
        # .9 格式的图片
        filp = kwargs.get('filp')
        self.image = QImage('Data/skin_aio_friend_bubble_pressed.9.png')
        if filp:
            self.image = self.image.mirrored(True, False)
        self.txt = kwargs.get('text')
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.adjustSize()

    def showEvent(self, event):
        super(Label, self).showEvent(event)
        pixmap = QtNinePatch2.createPixmapFromNinePatchImage(
            self.image, self.width(), self.height())
        self.setPixmap(pixmap)

    #
    def paintEvent(self, event) -> None:
        super(Label, self).paintEvent(event)
        painter = QPainter(self)
        painter.begin(self)
        painter.setPen(QColor(150, 100, 23))
        painter.setFont(QFont('SimSun', 20))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rec = QRectF(30, 40, self.width() - 60, self.height() - 60)
        painter.drawText(rec, Qt.TextWordWrap, self.txt)
        painter.end()

    #
    def resizeEvent(self, event):
        super(Label, self).resizeEvent(event)
        pixmap = QtNinePatch2.createPixmapFromNinePatchImage(
            self.image, self.width(), self.height())
        self.setPixmap(pixmap)


class BubbleMessage(QWidget):
    def __init__(self, text, avatar, isSend=False, parent=None):
        super().__init__(parent)
        self.isSend = isSend

        self.txt = text
        layout = QHBoxLayout()
        self.avatar = QLabel()
        self.avatar.setPixmap(avatar)
        self.message = Label(text=text, filp=isSend)
        if isSend:
            layout.addWidget(self.message)
            layout.addWidget(self.avatar, 0, Qt.AlignTop)
            layout.setStretch(0, 1)
        else:
            layout.addWidget(self.avatar, 0, Qt.AlignTop)
            layout.addWidget(self.message)
            layout.setStretch(1, 1)
        self.setLayout(layout)

    def resizeEvent(self, a0) -> None:
        w = (self.message.width() - 60) // 27
        row = int(len(self.txt) // w) + 1
        print('row', row)
        self.message.setMaximumHeight(row * 31 + 80)
        return


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        txt = '''在工具中单击边缘可以添加黑点，单击可以删掉黑点，拖动可以调整黑点长度。勾选等选项可以查看内容、缩放等区域右侧可预览不同拉伸情况下的效果，拖动可以调整预览的拉伸比例'''
        avatar = QPixmap('Data/head.jpg').scaled(60, 60)
        bubble_mesage = BubbleMessage(txt, avatar, isSend=False)
        layout = QVBoxLayout()
        bubble_mesage1 = BubbleMessage(txt, avatar, isSend=True)
        layout.addWidget(bubble_mesage)
        layout.addWidget(bubble_mesage1)
        # layout.setStretch(0, 1)
        self.setLayout(layout)


app = QApplication(sys.argv)
# w = Label()
w = MainWindow()
w.resize(400, 200)
w.show()

sys.exit(app.exec_())
