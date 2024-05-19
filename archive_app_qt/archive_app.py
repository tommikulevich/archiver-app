import os
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QVBoxLayout,
                             QPushButton, QMessageBox, QTreeView, QFileSystemModel, QScrollArea)

from archive_app_qt.archive_window import ArchiveWindowQt
from archive_app_qt.unarchive_window import UnarchiveWindowQt


class ArchiveAppQt(QMainWindow):
    def __init__(self):
        # Some window initialization
        super().__init__()
        self.setWindowTitle('Archiwizator z szyfrowaniem')
        self.setGeometry(300, 300, 600, 400)
        
        # Menu bar with "Information"
        mainMenu = self.menuBar()
        aboutAction = QAction('Informacja', self)
        aboutAction.triggered.connect(self.aboutDialog)
        mainMenu.addAction(aboutAction)
        
        # File browser
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(QtCore.QDir.rootPath()) 
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot | 
                                 QtCore.QDir.Files | QtCore.QDir.AllDirs)  
        self.fileBrowser = QTreeView()
        self.fileBrowser.setModel(self.fileModel)
        self.fileBrowser.setSelectionMode(QTreeView.MultiSelection)
        self.fileBrowser.setSelectionBehavior(QTreeView.SelectRows)
        self.fileBrowser.setExpandsOnDoubleClick(True)
        self.fileBrowser.viewport().installEventFilter(self)
        self.fileScrollArea = QScrollArea()
        self.fileScrollArea.setWidget(self.fileBrowser)
        self.fileScrollArea.setWidgetResizable(True)
        
        # Main buttons
        btnArchive = QPushButton('Zarchiwizować', self)
        btnArchive.clicked.connect(self.openArchiveWindow)
        
        btnUnarchive = QPushButton('Rozpakować', self)
        btnUnarchive.clicked.connect(self.openUnarchiveWindow)
        
        # Some layout stuff
        layout = QVBoxLayout()
        layout.addWidget(self.fileScrollArea)
        layout.addWidget(btnArchive)
        layout.addWidget(btnUnarchive)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def eventFilter(self, source, event):
        # Ensure user can choose files with Ctrl + Click
        if event.type() == event.MouseButtonPress and source is self.fileBrowser.viewport():
            modifiers = QApplication.keyboardModifiers()
            if modifiers != QtCore.Qt.ControlModifier:
                self.fileBrowser.clearSelection()
        return super().eventFilter(source, event)
    
    def aboutDialog(self):
        # Show info about application from file
        about_filename = "data/about.txt"
        
        about = "Archiwizator z szyfrowaniem."
        if os.path.exists(about_filename):
            with open(about_filename, 'r') as file:
                about = file.read()
            
        QMessageBox.about(self, "Opis aplikacji", about)

    def openArchiveWindow(self):
        # Get selected files
        selected_indexes = self.fileBrowser.selectedIndexes()
        selected_files = [self.fileModel.filePath(index) 
                          for index in selected_indexes 
                          if index.column() == 0]
        print("[Archive] Selected files", selected_files)
        
        # Check if any file was selected
        if not selected_files:
            QMessageBox.warning(self, "Błąd", "Nie wybrano plików.")
            return
        
        # Open Archive window
        self.archiveWindow = ArchiveWindowQt(self, selected_files)
        self.archiveWindow.show()

    def openUnarchiveWindow(self):
        # Get selected files
        selected_indexes = self.fileBrowser.selectedIndexes()
        selected_files = [self.fileModel.filePath(index) 
                          for index in selected_indexes 
                          if index.column() == 0]
        print("[Unarchive] Selected files", selected_files)
        
        # Check if any file was selected
        if not selected_files:
            QMessageBox.warning(self, "Błąd", "Nie wybrano archiwum.")
            return
        
        # Check archive extensions
        allowed_extensions = {".zip", ".7z", ".tar", ".tar.gz", ".tar.bz2", ".tar.xz"}
        extensions = {file.split('.')[-1].lower() for file in selected_files}
        if len(extensions) != 1 or f".{extensions.pop()}" not in allowed_extensions:
            QMessageBox.warning(self, "Błąd", "Jeśli chcesz rozpakować pliki, "
                "muszą one mieć to samo rozszerzenie: .zip, .7z lub .tar")
            return 
        
        # Open Unarchive window
        self.unarchiveWindow = UnarchiveWindowQt(self, selected_files)
        self.unarchiveWindow.show()
        