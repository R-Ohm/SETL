from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QDialog, QLabel, QDialogButtonBox, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from ui.pages.Translator_page_ui import Ui_Form
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QAbstractItemView, QMenu, QAction
from PyQt5.QtGui import QClipboard, QGuiApplication
import sqlite3
import os
import sys


class Translate(QWidget):
    def __init__(self):
        super(Translate, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Set the selection mode of the QListWidget to NoSelection
        self.ui.listWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.pushButton.clicked.connect(self.add_word_to_favourites)
        self.ui.pushButton_3.clicked.connect(self.add_word_to_database_window)
            
        # Connect the textChanged signal of the QLineEdit to the on_text_changed slot
        self.ui.lineEdit.textChanged.connect(self.on_text_changed)

        # Connect the returnPressed signal of the QLineEdit to the on_return_pressed slot
        self.ui.lineEdit.returnPressed.connect(self.on_return_pressed)

        # Create a context menu for the QListWidget
        self.ui.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listWidget.customContextMenuRequested.connect(self.show_context_menu)
    
    def showEvent(self, event):
        self.ui.listWidget.clear()
        # Connect to the SQLite database
        # Connect to the SQLite database
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_name = "data.db"
        db_path = os.path.join(sys._MEIPASS, db_name)
        # else:
        #     bundle_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(os.path.expanduser("~"), db_name)
        print(db_path)
        
        # db_path = os.path.join(bundle_dir, db_name)
        
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
    
        print("Reconnected to database successfully")

    def show_context_menu(self, pos):
        print("show_context_menu called")
        # Create a context menu
        menu = QMenu(self.ui.listWidget)

        # Add a "Copy" action to the context menu
        copy_action = QAction("Copy the definition", self.ui.listWidget)
        copy_action.setEnabled(self.ui.listWidget.currentItem() is not None)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)

        delete_action = QAction("Delete the definition", self.ui.listWidget)
        delete_action.setEnabled(self.ui.listWidget.currentItem() is not None)
        delete_action.triggered.connect(self.delete_selected_text)
        menu.addAction(delete_action)
        print("Delete action added to context menu")
        print("Current item:", self.ui.listWidget.currentItem())

        # Show the context menu at the cursor position
        menu.exec_(self.ui.listWidget.mapToGlobal(pos))

    def delete_selected_text(self):
        print("delete_selected_text called")
        # Get the selected text from the QListWidget
        selected_text = self.ui.listWidget.currentItem().text()

        # Delete the selected text from the SQLite database
        query = QSqlQuery()
        query.prepare("SELECT _id FROM entry WHERE headword=:word")
        query.bindValue(":word", selected_text)
        if not query.exec_():
            print("Error selecting entry ID:", query.lastError().text())
            return
        if not query.next():
            print("Entry not found:", selected_text)
            return
        entry_id = query.value(0)

        query.prepare("DELETE FROM entry WHERE _id=:id")
        query.bindValue(":id", entry_id)
        if not query.exec_():
            print("Error deleting entry:", query.lastError().text())
            return
        num_entries_deleted = query.numRowsAffected()
        self.db.commit()

        query.prepare("DELETE FROM translation WHERE entry_id=:id")
        query.bindValue(":id", entry_id)
        if not query.exec_():
            print("Error deleting translation:", query.lastError().text())
            return
        # self.ui.listWidget.clear()
        num_translations_deleted = query.numRowsAffected()
        self.db.commit()

        # QMessageBox.information(self, "Success", f"Deleted {num_entries_deleted} entries, {num_translations_deleted} translations")
    
    def copy_selected_text(self):
        # Get the selected text from the QListWidget
        selected_text = self.ui.listWidget.currentItem().text()
        
        # Copy the selected text to the clipboard
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(selected_text)


    def on_return_pressed(self):
        #call the on_text_changed function
        self.on_text_changed(self.ui.lineEdit.text())
    
    def add_word_to_database_window(self, word):
        #create a popup window
        dialog = QDialog(self.ui.widget)
        dialog.setWindowTitle("Add English Word")
        dialog.setStyleSheet("QDialog {background-color: #FBDA8A;} QDialog:title {color: white; font-size: 16px; font-weight: bold;}")

        #create the input box for English word and Thai word
        english_word_edit = QLineEdit()
        thai_definition_edit = QLineEdit()

        #auto input English text after click button
        # english_word_edit.setText(word)
        if isinstance(word, str):
            english_word_edit.setText(word)
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
        dialog.setLayout(layout)

        #connect to add word button to database
        add_button.clicked.connect(lambda: self.add_word_to_database(dialog ,english_word_edit, thai_definition_edit))

        #show the pop up window
        dialog.exec_()

    def add_word_to_database(self, dialog, english_word_edit, thai_definition_edit):
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
            QMessageBox.warning(dialog, "Word already exists", f"The word '{thai_definition_edit.text()}' already exists in '{english_word_edit.text()}'.")
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
            self.db.commit()

            QMessageBox.information(dialog, "Word added", f"The word '{english_word_edit.text()}' has been added to the database.")
            # self.on_text_changed(self.ui.listWidget)
            self.ui.listWidget.clear()
            self.db.commit()

        # Close the dialog
        dialog.accept()
    
    def add_word_to_favourites(self):
            
        print("add_word_to_favourites already!")
        english_word = self.ui.lineEdit.text()
        # print(english_word)

        if not english_word:
            self.ui.listWidget.clear()
            QMessageBox.information(self.ui.widget, "Error", "Please enter a word")
            return

        headword = None
        temp = None

        #create a SqlQuery to excute the database
        query = QSqlQuery()

        #execute a SQL query to retrieve data from the database
        query.prepare("SELECT entry.headword, translation.body, translation.entry_id FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{english_word}")
        query.exec_()

        #loop through the results of the query and print them to the console 
        while query.next():
            headword = query.value(0)
            english_word = query.value(1)
            word_id = query.value(2)
            # print(f"'{english_word}': {word_id}")
            # self.ui.listWidget.addItem(headword)
        
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
        
       
    def on_text_changed(self, text):

        # Convert the input text to lowercase or uppercase
        text = text.lower()  # or text.upper()

        if not text:
            self.ui.listWidget.clear()
            return

        #clear the listwidget
        self.ui.listWidget.clear()

        #create a SqlQuery to excute the database
        query = QSqlQuery()

        #execute a SQL query to retrieve data from the database
        query.prepare("SELECT entry.headword FROM translation JOIN entry ON translation.entry_id = entry._id WHERE translation.body = :word")
        query.bindValue(":word", f"{text}")
        query.exec_()     

        headword = None

        #loop through the results of the query and print them to the console
        while query.next():
            headword = query.value(0)
            self.ui.listWidget.addItem(headword)

        if headword is not None:
            print(f"Definition of '{text}': {headword}")
            query.prepare("INSERT INTO history (Word) VALUES (:Word)")
            query.bindValue(":Word", text)
            query.exec_()
            

        else:
            print(f"No definition found for '{text}'")
            item = QListWidgetItem(f"No definition found")
            font= QFont()
            font.setFamily("Poppins")
            font.setPointSize(12)
            item.setFont(font)
            self.ui.listWidget.addItem(item)

            # Add a message to prompt the user to add the word to the database
            message = QListWidgetItem("Want to add English Word?\n")
            font= QFont()
            font.setFamily("Poppins")
            font.setPointSize(12)
            message.setFont(font)
            self.ui.listWidget.addItem(message)

            #Create a QListWidgetItem object that contains the QPushButton object
            button = QPushButton("Add English Word here")
            font = QFont()
            font.setFamily("Poppins")
            font.setPointSize(12)
            button.setFont(font)
            
            button.setStyleSheet("QPushButton {border-radius: 24px; border: 2px solid #6CC48F;}")

            button.setFixedWidth(350)

            button.clicked.connect(lambda: self.add_word_to_database_window(text))

            add_data_btn = QListWidgetItem()
            add_data_btn.setSizeHint(button.sizeHint())
            self.ui.listWidget.addItem(add_data_btn)
            self.ui.listWidget.setItemWidget(add_data_btn, button)


        # print(f"Definition of '{text}': {headword}")