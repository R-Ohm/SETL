from PyQt5.QtWidgets import QWidget
from ui.pages.HIstory_page_ui import Ui_Form
class History(QWidget):
    def __init__(self):
        super(History, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


