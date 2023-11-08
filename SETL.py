from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFont
from ui.Main_interface_ui import Ui_MainWindow

#import the pages_functions
from page_functions.translate import Translate
from page_functions.vocabulary import Vocabulary
from page_functions.history import History
from page_functions.favourite import Favourite
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import sqlite3
import os
import shutil

class root(QMainWindow):
    def __init__(self):
        super(root, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## ======================
        ## Adding all pages
        ## ======================
        self.home_btn = self.ui.pushButton_4
        self.Vocabulary_button = self.ui.pushButton_3
        self.History_button = self.ui.pushButton_2
        self.Favourite_button = self.ui.pushButton
        
        ## ==================================================
        ## create menu buttons (nav bar) and variables
        ## ==================================================
        self.nav_button_dict = {
            self.home_btn: Translate,
            self.Vocabulary_button: Vocabulary,
            self.History_button: History,
            self.Favourite_button: Favourite,
        }

        ## ===========================================
        ## Show Translate page when the program opened
        ## ===========================================
        self.show_home_window()

        ## Set fonts
        font = QFont("Poppins", 12)
        self.ui.tabWidget.setFont(font)

        ## ===========================================
        ## Connect the buttons to the functions
        ## ===========================================
        self.home_btn.clicked.connect(self.show_home_window)
        self.Vocabulary_button.clicked.connect(self.show_selected_window)
        self.History_button.clicked.connect(self.show_selected_window)
        self.Favourite_button.clicked.connect(self.show_selected_window)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_name = "data.db"

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            db_path = os.path.join(sys._MEIPASS, db_name)
            # Copy the .db file to the user's home directory
            destination_path = os.path.join(os.path.expanduser("~"), db_name)
            if not os.path.exists(destination_path):
                shutil.copy2(db_path, os.path.expanduser("~"))
                print(f"Copied {db_path} to {destination_path}")
            else:
                print(f"Database file {destination_path} already exists")
        else:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)

        # Your existing code here...

        self.db.setDatabaseName(db_path)

        # Open the database connection
        if not self.db.open():
            print("Failed to open database")
            return
        else:
            print("Database opened successfully")


    def show_home_window(self):
        """
        show the Translate (home) page
        :return:
        """
        result = self.open_tab_flag(self.home_btn.text())
        self.set_btn_checked(self.home_btn)

        if result[0]:
            self.ui.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = self.home_btn.text()
            curIndex = self.ui.tabWidget.addTab(Translate(), tab_title)
            self.ui.tabWidget.setCurrentIndex(curIndex)
            self.ui.tabWidget.setVisible(True)

    
    def set_btn_checked(self, btn):
        """
        Set the button status
        :param btn: button object
        :return:
        """
        for button in self.nav_button_dict.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)
    
    def show_selected_window(self):
        """
        function for showing the selected page
        :return:
        """
        button = self.sender()
        result = self.open_tab_flag(button.text())
        self.set_btn_checked(button)

        if result[0]:
            self.ui.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = button.text()
            curIndex = self.ui.tabWidget.addTab(self.nav_button_dict[button](), tab_title)
            self.ui.tabWidget.setCurrentIndex(curIndex)
            self.ui.tabWidget.setVisible(True)


    def open_tab_flag(self, btn_text):
        """
        When the home page open the button should be selected
        :param btn_text: button text
        :return: bool and index
        """
        open_tab_count = self.ui.tabWidget.count()

        for i in range(open_tab_count):
            tab_title = self.ui.tabWidget.tabText(i)
            if tab_title == btn_text:
                return True, i
            else:
                continue
        return False,



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = root()
    window.show()
    sys.exit(app.exec_())