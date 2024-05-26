import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QVBoxLayout, QApplication, QStyle,
                             QFileDialog, QPushButton, QLabel, QCheckBox, 
                             QLineEdit, QProgressBar, QMessageBox, QDialog)

from archive_app_qt.worker import WorkerQt


class UnarchiveWindowQt(QDialog):
    def __init__(self, parent, selected_files):
        # Some window initialization
        super().__init__(parent)
        self.selected_files = selected_files
        self.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_FileDialogEnd)))
        self.setWindowTitle('Unarchive files')
        self.setGeometry(350, 350, 450, 250)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        layout = QVBoxLayout()
        
        # Delete files checkbox
        self.deleteFilesCheckbox = QCheckBox("Delete input files after completion")
        
        # Password
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Decryption password (optional).")
        self.passwordInput.setEchoMode(QLineEdit.Password)
        
        # Destination folder label and button
        self.destinationFolderLabel = QLabel("Destination folder: None selected")
        chooseDestFolderBtn = QPushButton("Choose folder")
        chooseDestFolderBtn.clicked.connect(self.chooseDestFolder)
                
        # Start button
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.startUnarchiving)
        
        # Progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0) 
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
        # Status label
        self.statusLabel = QLabel("Status: Waiting to start")
        
        # Some layout stuff
        layout.addWidget(self.deleteFilesCheckbox)
        layout.addWidget(self.passwordInput)
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

    def startUnarchiving(self):
        # Unachiving process: get all params
        delete_files = self.deleteFilesCheckbox.isChecked()
        password = self.passwordInput.text()
        
        # Check destination folder
        destination = self.destinationFolderLabel.text().replace("Destination folder: ", "")
        if not destination or destination == "None selected":
            QMessageBox.warning(self, "Error", "Destination folder not selected.")
            return
        
        # Run worker
        self.startButton.setEnabled(False)
        self.statusLabel.setText("Status: Processing...")
        self.worker = WorkerQt(
            mode='unarchive',
            files=self.selected_files,
            destination=destination,
            password=password,
            archive_name=None,
            delete_files=delete_files,
            format=None,
            compression_level=None
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