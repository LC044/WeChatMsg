class img_viewed(QWidget):

    def __init__(self, parent=None):
        super(img_viewed, self).__init__(parent)
        self.parent = parent
        self.width = 960
        self.height = 500

        self.scroll_ares_images = QScrollArea(self)
        self.scroll_ares_images.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget(self)
        self.scrollAreaWidgetContents.setObjectName('scrollAreaWidgetContends')

        # 进行网络布局
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.scroll_ares_images.setWidget(self.scrollAreaWidgetContents)

        self.scroll_ares_images.setGeometry(20, 50, self.width, self.height)
        self.vertocal1 = QVBoxLayout()

        # self.meanbar = QMenu(self)
        # self.meanbar.addMenu('&菜单')
        # self.openAct = self.meanbar.addAction('&Open',self.open)
        # self.startAct =self.meanbar.addAction('&start',self.start_img_viewer)
        self.open_file_pushbutton = QPushButton(self)
        self.open_file_pushbutton.setGeometry(150, 10, 100, 30)
        self.open_file_pushbutton.setObjectName('open_pushbutton')
        self.open_file_pushbutton.setText('打开文件夹...')
        self.open_file_pushbutton.clicked.connect(self.open)

        self.start_file_pushbutton = QPushButton(self)
        self.start_file_pushbutton.setGeometry(750, 10, 100, 30)
        self.start_file_pushbutton.setObjectName('start_pushbutton')
        self.start_file_pushbutton.setText('开始')
        self.start_file_pushbutton.clicked.connect(self.start_img_viewer)

        self.vertocal1.addWidget(self.scroll_ares_images)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    windo = img_viewed()
    windo.show()
    sys.exit(app.exec_())
