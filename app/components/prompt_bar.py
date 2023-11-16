from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PromptBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        def paintEvent(self, e):  # 绘图事件
            qp = QPainter()
            qp.begin(self)
            self.drawRectangles1(qp)  # 绘制线条矩形
            self.drawRectangles2(qp)  # 绘制填充矩形
            self.drawRectangles3(qp)  # 绘制线条+填充矩形
            self.drawRectangles4(qp)  # 绘制线条矩形2
            qp.end()

        def drawRectangles1(self, qp):  # 绘制填充矩形
            qp.setPen(QPen(Qt.black, 2, Qt.SolidLine))  # 颜色、线宽、线性
            qp.drawRect(*self.data)

        def drawRectangles2(self, qp):  # 绘制填充矩形
            qp.setPen(QPen(Qt.black, 2, Qt.NoPen))
            qp.setBrush(QColor(200, 0, 0))
            qp.drawRect(220, 15, 200, 100)

        def drawRectangles3(self, qp):  # 绘制线条+填充矩形
            qp.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            qp.setBrush(QColor(200, 0, 0))
            qp.drawRect(430, 15, 200, 100)

        def drawRectangles4(self, qp):  # 绘制线条矩形2
            path = QtGui.QPainterPath()
            qp.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            qp.setBrush(QColor(0, 0, 0, 0))  # 设置画刷颜色透明
            path.addRect(100, 200, 200, 100)
            qp.drawPath(path)
