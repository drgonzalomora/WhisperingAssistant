from PyQt5.QtWidgets import QMainWindow


class BaseWindowTemplate(QMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.initUI(**kwargs)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
