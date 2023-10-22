from PyQt5.QtWidgets import QWidget
from ui.pages.Favourite_page_ui import Ui_Form
class Favourite(QWidget):
    def __init__(self):
        super(Favourite, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


