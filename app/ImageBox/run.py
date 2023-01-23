from ui import MainDemo
from config import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    box = MainDemo()
    box.show()
    app.exec_()
