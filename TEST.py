from PyQt5 import QtCore, QtGui, QtWidgets
import time

class MyWindow(QtWidgets.QPushButton):

    def __init__(self):
        QtWidgets.QPushButton.__init__(self)
        self.setText("关闭窗口")
        self.clicked.connect(QtWidgets.qApp.quit)

    def load_data(self, sp):
        for i in range(1, 11):              #模拟主程序加载过程
            time.sleep(2)                   # 加载数据
            sp.showMessage("加载... {0}%".format(i * 10), QtCore.Qt.AlignHCenter |QtCore.Qt.AlignBottom, QtCore.Qt.black)
            QtWidgets.qApp.processEvents()  # 允许主进程处理事件

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap("img.jpg"))
    splash.showMessage("加载... 0%", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
    splash.show()                           # 显示启动界面
    QtWidgets.qApp.processEvents()          # 处理主进程事件
    window = MyWindow()
    window.setWindowTitle("QSplashScreen类使用")
    window.resize(300, 30)
    window.load_data(splash)                # 加载数据
    window.show()
    splash.finish(window)                   # 隐藏启动界面