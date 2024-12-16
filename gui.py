import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QProgressBar, 
                           QTextEdit, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor
from rsa_crypto import RSACrypto


class MatrixEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chars = "01"
        self.drops = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  
        
        # Initialize drops
        for i in range(30):  
            self.drops.append({
                'x': random.randint(0, 600),
                'y': random.randint(0, 100),
                'speed': random.randint(1, 3)
            })
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))  
        painter.setFont(QFont('Courier', 10))
        
        for drop in self.drops:
            # Draw random matrix character
            char = random.choice(self.chars)
            painter.setPen(QColor(0, 255, 0))  
            painter.drawText(drop['x'], drop['y'], char)
            
            # Update position
            drop['y'] += drop['speed']
            if drop['y'] > self.height():
                drop['y'] = 0
                drop['x'] = random.randint(0, self.width())  


class RansomwareWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rsa = RSACrypto()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('BlackHat Ransomware Simulator')
        self.setFixedSize(800, 600)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-family: 'Courier';
                min-width: 200px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: #000000;
            }
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
            }
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: 'Courier';
            }
            QProgressBar {
                border: 1px solid #00ff00;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel('RANSOMWARE SIMULATOR')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Courier', 24, QFont.Bold))
        title.setStyleSheet('color: #ff0000;')
        layout.addWidget(title)

        # BINARY CODE ANIMATION (with special area below the title)
        self.matrix_effect = MatrixEffect(self)
        self.matrix_effect.setFixedHeight(150)  
        layout.addWidget(self.matrix_effect)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setFixedHeight(150)
        self.status_display.append("System initialized and ready...")
        layout.addWidget(self.status_display)

        # Public Key and Private Key display
        self.public_key_label = QLabel("Public Key:")
        layout.addWidget(self.public_key_label)

        # Make public key copy-pasteable
        self.public_key_text = QLineEdit(f"{self.rsa.public_key}")
        self.public_key_text.setReadOnly(True)  
        layout.addWidget(self.public_key_text)

        self.private_key_label = QLabel("Private Key:")
        layout.addWidget(self.private_key_label)

        # Make private key copy-pasteable
        self.private_key_text = QLineEdit(f"{self.rsa.private_key[0]}")
        self.private_key_text.setReadOnly(True)  
        layout.addWidget(self.private_key_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Directory label
        self.dir_label = QLabel('No directory selected')
        self.dir_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dir_label)

        # Buttons
        self.select_btn = QPushButton('Select Target Directory')
        self.select_btn.clicked.connect(self.select_directory)
        layout.addWidget(self.select_btn)

        self.encrypt_btn = QPushButton('Encrypt Files')
        self.encrypt_btn.clicked.connect(self.start_encryption)
        layout.addWidget(self.encrypt_btn)

    def update_status(self, message):
        self.status_display.append(message)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selected_directory = directory
            self.dir_label.setText(f"Selected: {directory}")
            self.update_status(f"Directory selected: {directory}")

    def show_ransomware_popup(self):
        """Show a ransomware pop-up after encryption"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("""
        🚨 Your files have been encrypted! 🚨

        To recover your files, you must pay a ransom.

        Private Key: This is your decryption key. You must enter it below to decrypt your files.

        Failure to pay may result in permanent loss of your data.

        Enter your private key to recover your files.
        """)

        # Customize the pop-up theme
        msg.setWindowTitle("Ransomware - Files Encrypted")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0a0a0a;
            }
            QLabel {
                color: #ff0000;
                font-family: 'Courier';
                font-size: 14px;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #ff0000;
                border: 1px solid red;
                padding: 5px;
                font-family: 'Courier';
                min-width: 100px;
            }
        """)

        # Add input for private key in the pop-up
        key_input = QLineEdit(msg)
        key_input.setEchoMode(QLineEdit.Password)
        key_input.setPlaceholderText("Enter Private Key Here")
        msg.layout().addWidget(key_input)

        # Add button to confirm decryption
        button = msg.addButton("Decrypt Files", QMessageBox.AcceptRole)
        msg.exec_()

        # Check if correct key is entered
        if key_input.text() == str(self.rsa.private_key[0]):
            self.rsa.decrypt_directory(self.selected_directory)
            self.update_status("Decryption complete!")
            QMessageBox.information(self, "Decryption Complete", "Your files have been successfully decrypted!", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Invalid Key", "The private key you entered is incorrect. Please try again.", QMessageBox.Ok)

    def start_encryption(self):
        if not hasattr(self, 'selected_directory'):
            QMessageBox.warning(self, "Error", "Please select a directory first!")
            return

        self.worker = WorkerThread(self.rsa, self.selected_directory, 'encrypt')
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.show_ransomware_popup)  
        self.worker.start()


class WorkerThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, rsa, directory, mode='encrypt'):
        super().__init__()
        self.rsa = rsa
        self.directory = directory
        self.mode = mode

    def run(self):
        try:
            if self.mode == 'encrypt':
                self.progress.emit("Starting encryption...")
                self.rsa.encrypt_directory(self.directory)
                self.progress.emit("Encryption complete!")
            else:
                self.progress.emit("Starting decryption...")
                self.rsa.decrypt_directory(self.directory)
                self.progress.emit("Decryption complete!")
            self.finished.emit()
        except Exception as e:
            self.progress.emit(f"Operation failed: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RansomwareWindow()
    window.show()
    sys.exit(app.exec_())
