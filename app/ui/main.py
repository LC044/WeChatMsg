import os
import sys

from ui_interface import *
import resources_rc

from PyQt5.QtWidgets import QApplication, QMainWindow

from Custom_Widgets.Widgets import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        loadJsonStyle(self, self.ui)
        
        self.show()
        
        self.ui.toolBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.msgBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.friendBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.userBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        
        self.ui.aboutBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.helpBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.settingBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        
        self.ui.closeCenterMenuBtn.clicked.connect(lambda: self.ui.centerMenuContainer.collapseMenu())
        
        self.ui.closeNotificationBtn.clicked.connect(lambda: self.ui.popupNotificationsContainer.collapseMenu())
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())