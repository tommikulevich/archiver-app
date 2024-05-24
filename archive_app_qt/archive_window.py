import os
import re
import platform
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (QVBoxLayout, QFileDialog, QPushButton, QLabel, 
                             QComboBox, QCheckBox, QLineEdit, QProgressBar, 
                             QMessageBox, QDialog)

from archive_app_qt.worker import WorkerQt


class ArchiveWindowQt(QDialog):
    def __init__(self, parent, selected_files):
        # Some window initialization
        super().__init__(parent)
        self.selected_files = selected_files
        self.setWindowTitle('Archive the files')
        self.setGeometry(350, 350, 450, 300)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        layout = QVBoxLayout()
        
        # Archive format label and combo box
        self.archiveFormatLabel = QLabel("Archive format:")
        self.archiveFormat = QComboBox()
        self.archiveFormat.addItems([".zip", ".7z", ".tar"])
        
        # Compression level label and combo box
        self.compressionLevelLabel = QLabel("Compression level:")
        self.compressionLevel = QComboBox()
        self.compressionLevel.addItems(["Fast", "Normal", "Maximum"])
        
        # Delete files checkbox
        self.deleteFilesCheckbox = QCheckBox("Delete input files after completion")
        
        # Password
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Encryption password (optional)")
        self.passwordInput.setEchoMode(QLineEdit.Password)
        
        # Archive name
        self.archiveNameInput = QLineEdit()
        self.archiveNameInput.setPlaceholderText("Archive name")
        
        # Destination folder label and button
        self.destinationFolderLabel = QLabel("Destination folder: None selected")
        chooseDestFolderBtn = QPushButton("Choose folder")
        chooseDestFolderBtn.clicked.connect(self.chooseDestFolder)
        
        # Start button
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.startArchiving)
        
        # Progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0) 
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
        # Status label
        self.statusLabel = QLabel("Status: Waiting to start")
        
        # Some layout stuff
        layout.addWidget(self.archiveFormatLabel)
        layout.addWidget(self.archiveFormat)
        layout.addWidget(self.compressionLevelLabel)
        layout.addWidget(self.compressionLevel)
        layout.addWidget(self.deleteFilesCheckbox)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.archiveNameInput)
        layout.addWidget(chooseDestFolderBtn)
        layout.addWidget(self.destinationFolderLabel)
        layout.addWidget(self.startButton)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.statusLabel)

        self.setLayout(layout)

    def chooseDestFolder(self):
        # Choosing destination folder
        folder = QFileDialog.getExistingDirectory(self, "Choose destination folder")
        if folder:
            self.destinationFolderLabel.setText(f"Destination folder: {folder}")

    def startArchiving(self):
        # Achiving process: get all params
        format = self.archiveFormat.currentText()
        compression_level = self.compressionLevel.currentText()
        delete_files = self.deleteFilesCheckbox.isChecked()
        
        # Check password
        password = self.passwordInput.text()
        if not password:
            reply = QMessageBox.question(self, "Warning", 
                                         "No password. Continue without encryption?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Check archive name
        archive_name = self.archiveNameInput.text()
        if not archive_name:
            QMessageBox.warning(self, "Error", "No archive name entered.")
            return
        
        invalid_chars = r'<>:"\\/|?*' if platform.system() == 'Windows' else r'/'
        invalid_chars_pattern = f"[{re.escape(invalid_chars)}]"
        if len(archive_name) > 255 or re.search(invalid_chars_pattern, archive_name):
            QMessageBox.warning(self, "Error", "This archive name is not allowed.")
            return

        # Check destination folder
        destination = self.destinationFolderLabel.text().replace("Destination folder: ", "")
        if not destination or destination == "None selected":
            QMessageBox.warning(self, "Error", "Destination folder not selected.")
            return
        
        # Check if there is no files with selected name in destination folder
        archive_filename = f"{archive_name}{format}"
        archive_path = os.path.join(destination, archive_filename)
        if os.path.exists(archive_path):
            QMessageBox.warning(self, "Error", f"File with name '{archive_filename}'"
                                "already exists in destination folder.")
            return

        # Run worker
        self.startButton.setEnabled(False)
        self.statusLabel.setText("Status: Processing...")
        self.worker = WorkerQt(
            mode='archive',
            files=self.selected_files,
            destination=destination,
            password=password,
            archive_name=archive_name,
            delete_files=delete_files,
            format=format,
            compression_level=compression_level
        )
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.error.connect(self.showError)
        self.worker.finished.connect(self.taskCompleted)
        self.worker.start()

    def showError(self, message):
        QMessageBox.critical(self, "Error", message)
        self.progressBar.setValue(0)
        self.statusLabel.setText("Status: Error")
        self.startButton.setEnabled(True)

    def taskCompleted(self):
        if self.progressBar.value() == 100:
            QMessageBox.information(self, "Completed", "Operation completed successfully.")

        self.progressBar.setValue(0)
        self.statusLabel.setText("Status: Waiting to start")
        self.startButton.setEnabled(True)