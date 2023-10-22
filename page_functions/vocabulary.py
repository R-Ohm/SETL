from PyQt5.QtWidgets import QWidget
from ui.pages.Vocabulary_page_ui import Ui_Form
class Vocabulary(QWidget):
    def __init__(self):
        super(Vocabulary, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


