#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2020年3月13日
@author: Irony
@site: https://pyqt.site , https://github.com/PyQt5
@email: 892768447@qq.com
@file: Demo.Lib.QCursorGif
@description: 
"""

try:
    from PyQt5.QtCore import QTimer, Qt
    from PyQt5.QtGui import QCursor, QPixmap
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PySide2.QtCore import QTimer, Qt
    from PySide2.QtGui import QCursor, QPixmap
    from PySide2.QtWidgets import QApplication
from app.resources import resource_rc

var = resource_rc.qt_resource_name


class QCursorGif:

    def initCursor(self, cursors, parent=None):
        # 记录默认的光标
        self._oldCursor = Qt.ArrowCursor
        self.setOldCursor(parent)
        # 加载光标图片
        self._cursorImages = [
            QCursor(QPixmap(cursor)) for cursor in cursors]
        self._cursorIndex = 0
        self._cursorCount = len(self._cursorImages) - 1
        # 创建刷新定时器
        self._cursorTimeout = 200
        self._cursorTimer = QTimer(parent)
        self._cursorTimer.timeout.connect(self._doBusy)
        self.num = 0

    def _doBusy(self):
        if self._cursorIndex > self._cursorCount:
            self._cursorIndex = 0
        QApplication.setOverrideCursor(
            self._cursorImages[self._cursorIndex])
        self._cursorIndex += 1
        self.num += 1

    def startBusy(self):
        # QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self._cursorTimer.isActive():
            self._cursorTimer.start(self._cursorTimeout)

    def stopBusy(self):
        self._cursorTimer.stop()
        QApplication.restoreOverrideCursor()
        # 将光标出栈，恢复至原始状态
        for i in range(self.num):
            QApplication.restoreOverrideCursor()
        self.num = 0


    def setCursorTimeout(self, timeout):
        self._cursorTimeout = timeout

    def setOldCursor(self, parent=None):
        QApplication.overrideCursor()
        self._oldCursor = (QApplication.overrideCursor() or parent.cursor() or Qt.ArrowCursor or Qt.IBeamCursor) if parent else (
                QApplication.overrideCursor() or Qt.ArrowCursor)
