import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QEvent, QObject


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        loadUi("OverlayMask.ui", self)

        # Saves the mouse relative position for detecting mouse events
        self.mouse_relative_position_x = 0
        self.mouse_relative_position_y = 0

        # When button is clicked, then close the window
        self.closeButton.clicked.connect(self.close)

        # Gives the user ability to drag window 
        self.centralwidget.setMouseTracking(True)
        self.centralwidget.installEventFilter(self)

        # Produces a red border along the window
        self.centralwidget.setStyleSheet("border-color: rgba(255, 0, 0, 255);")
        
        # Produces a transparent border along the window
        # self.centralwidget.setStyleSheet("border-color: rgba(255, 255, 255, 2);")

    # Override method mousePressEvent for class MainWindow
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get the cursor position relative to the window that receives the mouse event
            self.mouse_relative_position_x = event.pos().x()
            self.mouse_relative_position_y = event.pos().y()

    # Override method mouseReleaseEvent for class MainWindow
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Changes the mouse cursor to be the standard icon
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    # Override method eventFilter for class MainWindow
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        # If the mouse moved.
        if event.type() == QEvent.MouseMove:
            # Events for when the mouse left button is pressed
            if event.buttons() & Qt.LeftButton:
                # Changes the mouse cursor to become a move cursor icon 
                QApplication.setOverrideCursor(Qt.SizeAllCursor)
                # Moves the window when the mouse is dragged
                self.move(event.globalPos().x() - self.mouse_relative_position_x,
                          event.globalPos().y() - self.mouse_relative_position_y)
            else:
                return False
        else:
            return False
        return True


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
 	
 	# Produces a borderless window
    window.setWindowFlags(Qt.FramelessWindowHint)

    # This indicates that the widget should have a translucent background
    window.setAttribute(Qt.WA_TranslucentBackground)

    # Maximizes the window 
    window.showMaximized()


    try:
    	sys.exit(app.exec_())
    except:
    	print("Exiting")


if __name__ == '__main__':
    main()