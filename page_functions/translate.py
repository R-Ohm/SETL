from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from ui.pages.Translator_page_ui import Ui_Form
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QAbstractItemView, QMenu, QAction
from PyQt5.QtGui import QClipboard, QGuiApplication


class Translate(QWidget):
    def __init__(self):
        super(Translate, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Set the selection mode of the QListWidget to NoSelection
        self.ui.listWidget.setSelectionMode(QAbstractItemView.NoSelection)

        # Connect to the SQLite database
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("English_Thai_vocab.sqlite")
        if not db.open():
            print("Failed to connect to database")
            return
        else:
            print("Connected to database")

        # Connect the textChanged signal of the QLineEdit to the on_text_changed slot
        self.ui.lineEdit.textChanged.connect(self.on_text_changed)

        # Connect the returnPressed signal of the QLineEdit to the on_return_pressed slot
        self.ui.lineEdit.returnPressed.connect(self.on_return_pressed)

        # Create a context menu for the QListWidget
        self.ui.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listWidget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        # Create a context menu
        menu = QMenu(self.ui.listWidget)

        # Add a "Copy" action to the context menu
        copy_action = QAction("Copy the definition", self.ui.listWidget)
        copy_action.setEnabled(self.ui.listWidget.currentItem() is not None)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)

        # Show the context menu at the cursor position
        menu.exec_(self.ui.listWidget.mapToGlobal(pos))

    
    def copy_selected_text(self):
        # Get the selected text from the QListWidget
        selected_text = self.ui.listWidget.currentItem().text()
        
        # Copy the selected text to the clipboard
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(selected_text)


    def on_return_pressed(self):
        #call the on_text_changed function
        self.on_text_changed(self.ui.lineEdit.text())

    def on_text_changed(self, text):

        # Convert the input text to lowercase or uppercase
        text = text.lower()  # or text.upper()
        
        #clear the listwidget
        self.ui.listWidget.clear()

        #create a SqlQuery to excute the database
        query = QSqlQuery()

        #execute a SQL query to retrieve data from the database
        query.prepare("SELECT entry.headword FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{text}")
        query.exec_()     

        headword = ""

        #loop through the results of the query and print them to the console
        while query.next():
            headword = query.value(0)
            self.ui.listWidget.addItem(headword)

        print(f"Definition of '{text}': {headword}")