from PyQt5.QtWidgets import QWidget
from ui.pages.Translator_page_ui import Ui_Form

class Translate(QWidget):
    def __init__(self):
        super(Translate, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


