from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.Main_interface_ui import Ui_MainWindow

class root(QMainWindow):
    def __init__(self):
        super(root, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = root()
    window.show()
    sys.exit(app.exec_())