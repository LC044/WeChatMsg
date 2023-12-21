from PyQt5.QtWidgets import QScrollBar


class ScrollBar(QScrollBar):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            '''
          QScrollBar:vertical {
              border-width: 0px;
              border: none;
              background:rgba(133, 135, 138, 0);
              width:4px;
              margin: 0px 0px 0px 0px;
          }
          QScrollBar::handle:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 rgb(133, 135, 138), stop: 0.5 rgb(133, 135, 138), stop:1 rgb(133, 135, 138));
              min-height: 20px;
              max-height: 20px;
              margin: 0 0px 0 0px;
              border-radius: 2px;
          }
          QScrollBar::add-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 rgba(133, 135, 138, 0), stop: 0.5 rgba(133, 135, 138, 0),  stop:1 rgba(133, 135, 138, 0));
              height: 0px;
              border: none;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0  rgba(133, 135, 138, 0), stop: 0.5 rgba(133, 135, 138, 0),  stop:1 rgba(133, 135, 138, 0));
              height: 0 px;
              border: none;
              subcontrol-position: top;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-page:vertical {
              background: rgba(133, 135, 138, 0);
          }

          QScrollBar::add-page:vertical {
              background: rgba(133, 135, 138, 0);
          }
            '''
        )