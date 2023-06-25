import sys 
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow

# This file contains all the functionalities of the widgets between the windows

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("MainWindow.ui", self)
        self.MaskFeed_btn.clicked.connect(self.gotoMaskFeedWindow)
        self.GeometryEdit_btn.clicked.connect(self.gotoGeometryEditingWindow)
        self.ProjectorConfig_btn.clicked.connect(self.gotoProjectorConfigurationWindow)

    def gotoMaskFeedWindow(self):
        maskFeed = MaskFeedWindow()
        widget.addWidget(maskFeed)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoGeometryEditingWindow(self):
        geometryEdit = GeometryEditingWindow()
        widget.addWidget(geometryEdit)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoProjectorConfigurationWindow(self):
        projectorConfig = ProjectorConfigurationWindow()
        widget.addWidget(projectorConfig)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class MaskFeedWindow(QMainWindow):
    def __init__(self):
        super(MaskFeedWindow, self).__init__()
        loadUi("MaskFeedWindow.ui", self)
        self.Back_btn.clicked.connect(self.gotoMainWindow)

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class GeometryEditingWindow(QMainWindow):
    def __init__(self):
        super(GeometryEditingWindow, self).__init__()
        loadUi("GeometryEditingWindow.ui", self)
        self.Back_btn.clicked.connect(self.gotoMainWindow)

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class ProjectorConfigurationWindow(QMainWindow):
    def __init__(self):
        super(ProjectorConfigurationWindow, self).__init__()
        loadUi("ProjectorConfigurationWindow.ui", self)
        self.Back_btn.clicked.connect(self.gotoMainWindow)

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    mainWindow = MainWindow()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(600)
    widget.setFixedWidth(900)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
