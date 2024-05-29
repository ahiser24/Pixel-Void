import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFileDialog, QProgressDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from rembg import remove
from PIL import Image

class BackgroundRemoverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Pixel Void')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('_internal/images/icon.ico'))  # Set the path to your .ico file

        # Main layout (vertical)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Logo
        logo = QLabel(self)
        logo.setPixmap(QPixmap('_internal/images/logo.png').scaled(200, 200, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo)

        # Image section layout (horizontal)
        image_layout = QHBoxLayout()
        image_layout.setAlignment(Qt.AlignCenter)

        # Left side - Image upload section
        left_layout = QVBoxLayout()
        self.image_label = QLabel('Upload an Image')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("font-size: 16px; color: #ffffff; border: 2px dashed #ccc; padding: 20px;")
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAcceptDrops(True)
        self.setAcceptDrops(True)  # Make sure the main window accepts drops
        left_layout.addWidget(self.image_label)

        image_layout.addLayout(left_layout)

        # Right side - Preview Section
        right_layout = QVBoxLayout()

        self.preview_label = QLabel('Image Preview')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setStyleSheet("font-size: 16px; color: #ffffff; border: 2px solid #ffffff; padding: 10px;")
        right_layout.addWidget(self.preview_label)

        image_layout.addLayout(right_layout)
        main_layout.addLayout(image_layout)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.upload_btn = QPushButton('Choose File')
        self.upload_btn.setStyleSheet("background-color: #007BFF; color: white; border-radius: 5px; padding: 10px;")
        self.upload_btn.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_btn)

        self.remove_bg_btn = QPushButton('Remove Background')
        self.remove_bg_btn.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px; padding: 10px;")
        self.remove_bg_btn.clicked.connect(self.remove_background)
        button_layout.addWidget(self.remove_bg_btn)

        main_layout.addLayout(button_layout)

        # Bottom section - Output information
        self.output_label = QLabel('')
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        self.output_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.output_label.setOpenExternalLinks(True)
        main_layout.addWidget(self.output_label)

        self.setStyleSheet("background-color: #160f1f; color: white")
        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg')):
                self.image_path = file_path
                self.image_label.setPixmap(QPixmap(file_path).scaled(300, 300, Qt.KeepAspectRatio))
                self.output_label.setText('')
                self.preview_label.setText('Image Preview')
                self.preview_label.setPixmap(QPixmap())
                break

    def upload_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose an Image", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_name:
            self.image_path = file_name
            self.image_label.setPixmap(QPixmap(file_name).scaled(300, 300, Qt.KeepAspectRatio))
            self.output_label.setText('')
            self.preview_label.setText('Image Preview')
            self.preview_label.setPixmap(QPixmap())

    def remove_background(self):
        if hasattr(self, 'image_path'):
            progress_dialog = QProgressDialog("Removing background...", "Cancel", 0, 100, self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.setValue(0)
            progress_dialog.setFixedSize(400, 100)

            progress_dialog.setStyleSheet("QProgressDialog > QLabel { color: #ffffff; }")
            QApplication.processEvents()

            try:
                input_image = Image.open(self.image_path)
                output_image = remove(input_image)

                output_path = os.path.join(os.path.dirname(self.image_path), f"output_{os.path.splitext(os.path.basename(self.image_path))[0]}.png")
                output_image.save(output_path, 'PNG')

                progress_dialog.setValue(100)
                self.output_label.setText(f"<a href=\"file:///{output_path}\">Background removed and saved at: {output_path}</a>")
                self.preview_label.setText('')
                self.preview_label.setPixmap(QPixmap(output_path).scaled(300, 300, Qt.KeepAspectRatio))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while removing the background: {str(e)}")
            finally:
                progress_dialog.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BackgroundRemoverApp()
    ex.show()
    sys.exit(app.exec_())
