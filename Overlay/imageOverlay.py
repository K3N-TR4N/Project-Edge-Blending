import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QEvent, QObject

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Image Window")

        # Load the image
        self.image_path = "Mask.png"
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(self.image_path))

        # Set the image label as the central widget
        self.setCentralWidget(self.image_label)


if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = ImageWindow()

    # Produces a borderless window
    window.setWindowFlags(Qt.FramelessWindowHint)

    # This indicates that the widget should have a translucent background
    window.setAttribute(Qt.WA_TranslucentBackground)

    # Maximizes the window 
    window.showMaximized()
    # Start the event loop
    sys.exit(app.exec())