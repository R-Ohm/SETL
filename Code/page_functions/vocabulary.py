from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QDialog, QLabel, QDialogButtonBox, QMessageBox
from ui.pages.Vocabulary_page_ui import Ui_Form
from ui.pages.Modify_dialog_ui import Ui_Dialog
from PyQt5.QtGui import QFont
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QHBoxLayout, QAbstractItemView, QMenu, QAction
import sqlite3
from PyQt5.QtCore import Qt, QSize
import os
import sys

class Modify_dialog(QDialog):
    def __init__(self, parent=None):
        super(Modify_dialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        #if click the checkbox will be enable too
        self.ui.listWidget.itemClicked.connect(self.enable_checkbox)

    def enable_checkbox(self, item):
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        
    

class Vocabulary(QWidget):
    def __init__(self):
        super(Vocabulary, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #Add search box
        self.ui.lineEdit.textChanged.connect(self.search)
        self.ui.listWidget.itemDoubleClicked.connect(self.show_dialog)


    def showEvent(self, event):
        self.ui.listWidget.clear()
        # Connect to the SQLite database
        # Connect to the SQLite database
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_name = "data.db"
        db_path = os.path.join(os.path.expanduser("~"), db_name)
        print(db_path)
        
        if not os.path.exists(db_path):
            print(f"Database file {db_path} does not exist")
            return
        else:
            print("Connected to database")
        
        self.db.setDatabaseName(db_path)

        # Open the database connection
        if not self.db.open():
            print("Failed to open database")
            return
        else:
            print("Database opened successfully")

        query = QSqlQuery()
        #Choose the vocab by filtering to show only one word vocab
        query.prepare("SELECT DISTINCT body from translation")
        query.exec_()

        while query.next():
            english_word = query.value(0)
            self.ui.listWidget.addItem(english_word)
    
        print("Reconnected to database successfully")
    
    def search(self, text):
        #find words from listWidget
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            if item.text().lower().startswith(text.lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def show_dialog(self, item):
        dialog = Modify_dialog(self)
        dialog.ui.label.setText(item.text())
        dialog.setStyleSheet("QDialog {background-color: #FFF9F1;} QDialog:title {color: white; font-size: 16px; font-weight: bold;}")
        query = QSqlQuery()
        query.prepare("SELECT entry.headword FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{item.text()}")
        query.exec_()   
        headword = None
        while query.next():
            headword = query.value(0)
            dialog.ui.listWidget.addItem(headword)
        
        #add checkbox for multiple choosing in listWidget
        for i in range(dialog.ui.listWidget.count()):
            definition_item = dialog.ui.listWidget.item(i)
            definition_item.setFlags(definition_item.flags() | Qt.ItemIsUserCheckable)
            definition_item.setCheckState(Qt.Unchecked)
        # print(definition_item.text())
        Font = QFont()
        Font.setFamily("Poppins")
        Font.setPointSize(14)
        dialog.ui.listWidget.setFont(Font)
        
        #button for add definition to database
        dialog.ui.pushButton_3.clicked.connect(lambda: self.add_word_to_database_window(item, dialog, headword))

        #button for delete the definition from database
        dialog.ui.pushButton.clicked.connect(lambda: self.delete_word_from_selection(dialog, item))

        dialog.finished.connect(lambda: self.reconnect_Eng_data(item))
        
        dialog.ui.pushButton_2.clicked.connect(lambda: self.add_word_to_favourites(dialog, item))

        dialog.exec_()

    def add_word_to_database_window(self, item, dialog, headword):
        #create a popup window
        popup = QDialog(self.ui.widget)
        popup.setWindowTitle("Add English Word")
        popup.setStyleSheet("QDialog {background-color: #FBDA8A;} QDialog:title {color: white; font-size: 16px; font-weight: bold;}")

        #create the input box for English word and Thai word
        english_word_edit = QLineEdit()
        thai_definition_edit = QLineEdit()

        #auto input English text after click button
        if isinstance(item.text(), str):
            english_word_edit.setText(item.text())
        else:
             english_word_edit.setText("")

        #create explaination text
        english_word_label = QLabel("English Word:")
        thai_definition_label = QLabel("Thai Definition:")

        font= QFont()
        font.setFamily("Poppins")
        font.setPointSize(12)
        english_word_edit.setFont(font)
        thai_definition_edit.setFont(font)
        english_word_label.setFont(font)
        thai_definition_label.setFont(font)

        #create button
        add_button = QPushButton("Add to database")
        add_button.setFont(font)


        #create layout
        layout = QHBoxLayout()
        layout.addWidget(english_word_label)
        layout.addWidget(english_word_edit)
        layout.addWidget(thai_definition_label)
        layout.addWidget(thai_definition_edit)
        layout.addWidget(add_button)
        popup.setLayout(layout)

        #connect to add word button to database
        add_button.clicked.connect(lambda: self.add_word_to_database(popup , item, english_word_edit, thai_definition_edit, dialog, headword))

        #show the pop up window
        popup.exec_()

    def add_word_to_database(self, popup, item, english_word_edit, thai_definition_edit, dialog, headword):
        # Create a QSqlQuery object to execute SQL queries on the database
        query = QSqlQuery()

        # Execute a SQL query to retrieve the ID of the English word, if it already exists in the database
        query.prepare("SELECT _id FROM translation WHERE body = :body AND entry_id IN (SELECT _id FROM entry WHERE headword = :headword)")
        query.bindValue(":body", english_word_edit.text())
        query.bindValue(":headword", thai_definition_edit.text())
        query.exec_()

        # Check if the query returned a result
        if query.next():
            # The English word already exists in the database, show an error message to the user
            QMessageBox.warning(popup, "Word already exists", f"The word '{thai_definition_edit.text()}' already exists in '{english_word_edit.text()}'.")
        else:
            # The English word does not exist in the database, insert the Thai and English words
            query.prepare("INSERT INTO entry (headword) VALUES (:headword)")
            query.bindValue(":headword", thai_definition_edit.text())
            query.exec_()
            self.db.commit()

            # Get the ID of the last inserted row in the entry table
            entry_id = query.lastInsertId()

            query.prepare("INSERT INTO translation (body, entry_id) VALUES (:body,:entry_id)")
            query.bindValue(":body", english_word_edit.text())
            query.bindValue(":entry_id", entry_id)
            query.exec_()
            self.db.commit()

            print(f"English word: {english_word_edit.text()}")
            print(f"Thai definition: {thai_definition_edit.text()}")
            print(f"id: {entry_id}")

            QMessageBox.information(popup, "Word added", f"The word '{english_word_edit.text()}' has been added to the database.")
            dialog.ui.listWidget.clear()
            query.prepare("SELECT entry.headword FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
            query.bindValue(":word", f"{item.text()}")
            query.exec_()   
            # headword = None
            while query.next():
                headword = query.value(0)
                dialog.ui.listWidget.addItem(headword)
            


        # Close the dialog
        popup.accept()

    
    def delete_word_from_selection(self, dialog, item):
        # Create a QSqlQuery object to execute SQL queries on the database
        query = QSqlQuery()

        # Print the selection item in an array
        selected = []
        for i in range(dialog.ui.listWidget.count()):
            item_selected = dialog.ui.listWidget.item(i)
            if item_selected.checkState() == Qt.Checked:
                selected.append(item_selected.text())

        # Delete the word from the database
        for i in range(len(selected)):
            query.prepare("SELECT _id FROM entry WHERE headword = :headword")
            query.bindValue(":headword", selected[i])
            query.exec_()
            
            if query.next():
                entry_id = query.value(0)
                # print(f"Deleted {selected[i]}")
                
                query.prepare("DELETE FROM entry WHERE _id = :id")
                query.bindValue(":id", entry_id)
                query.exec_()
                self.db.commit()
                query.prepare("DELETE FROM translation WHERE entry_id = :id")
                query.bindValue(":id", entry_id)
                query.exec_()
                self.db.commit()
                
            else:
                print(f"Entry not found for {selected[i]}")

        dialog.ui.listWidget.clear()
        print("clear")
       
        query.prepare("SELECT entry.headword FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{item.text()}")
        query.exec_()
        
        # Clear the selected list and repopulate the listWidget
        while query.next():
            headword = query.value(0)
            dialog.ui.listWidget.addItem(headword)
        
        item_selected = None
        selected = []
        

    def reconnect_Eng_data(self, item):
        query = QSqlQuery()
        query.prepare("SELECT DISTINCT body from translation")
        query.exec_()
        self.ui.listWidget.clear()
        while query.next():
            english_word = query.value(0)
            self.ui.listWidget.addItem(english_word)

    def add_word_to_favourites(self, dialog, item):
        print("_________________________")
        print("add word to favourites")
        query = QSqlQuery()
        headword = None
        english_word = None
        word_id = None
        temp = None
        
        #execute a SQL query to retrieve data from the database
        query.prepare("SELECT entry.headword, translation.body, translation.entry_id FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{item.text()}")
        query.exec_()
        print("1")

        while query.next():
            headword = query.value(0)
            english_word = query.value(1)
            word_id = query.value(2)

        query.prepare("SELECT Word FROM favourite WHERE Word = :word")
        query.bindValue(":word", english_word)
        query.exec_()

        while query.next():
            temp = query.value(0)
        
        if temp == english_word:
            print("You have already added this word to your favourite list")
            QMessageBox.information(self, "Sorry :(", f"You have already added '{english_word}' to your favourite list.")
            return


        if headword is not None:
            print("yay!")
            
            query.prepare("INSERT INTO favourite (entry_id,Word) VALUES (:entry_id,:Word)")
            query.bindValue(":entry_id", word_id)
            query.bindValue(":Word", english_word)
            query.exec_()
            self.db.commit()
            QMessageBox.information(self, "Word added", f"The word '{english_word}' has been added to the database.")

        else:
            print("no!")
            QMessageBox.information(self, "Sorry :(", f"The word '{english_word}' doesn't have definition.")
            dialog.accept()
        




