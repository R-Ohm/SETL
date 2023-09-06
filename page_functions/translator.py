from PyQt5.QtWidgets import QWidget
from ui.pages.Translator_page_ui import Ui_Translate

class Translator(Qwidget):
    def __init__(self):
        super(Translator, self).__init__()
        self.ui = Ui_Translate()
        self.ui.setupUi(self)


