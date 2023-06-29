import sys 
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox

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
        self.Add_btn.clicked.connect(self.addClient)
        self.Edit_btn.clicked.connect(self.editClient)
        self.Delete_btn.clicked.connect(self.deleteClient)
        self.listClients()
        self.Client_list.itemClicked.connect(self.listItemClicked)

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def listClients(self):
        self.Client_list.clear()
        with open("client_ip.txt", "r") as clients:
            ips = clients.readlines()
        for ip in ips:
            if ip[0] == "#":
                continue
            else:
                self.Client_list.addItem(ip.strip())
        self.Edit_name.setEnabled(False)
        self.Edit_IP.setEnabled(False)
        self.Edit_btn.setEnabled(False)
        self.Delete_btn.setEnabled(False)

    def listItemClicked(self):
        self.Edit_name.setEnabled(True)
        self.Edit_IP.setEnabled(True)
        self.Edit_btn.setEnabled(True)
        self.Delete_btn.setEnabled(True)
        

    def addClient(self):
        if self.Add_name.toPlainText() != "" and self.Add_IP.toPlainText() != "":
            with open("client_ip.txt", "a") as clients:
                clients.write("\n" + self.Add_name.toPlainText() + " - " + self.Add_IP.toPlainText())
            self.listClients()

    def editClient(self):
        if self.Edit_name.toPlainText() != "" and self.Edit_IP.toPlainText() != "":
            clients = open("client_ip.txt", "r")
            ips = clients.readlines()
            clients.close()
            for i in range(len(ips)):
                if ips[i].strip() == self.Client_list.currentItem().text().strip():
                    ips[i] = self.Edit_name.toPlainText() + " - " + self.Edit_IP.toPlainText() + "\n"
                    break
            clients = open("client_ip.txt", "w")
            for ip in ips:
                 clients.write(ip)
            clients.close()
            self.listClients()
    
    def deleteClient(self):
        confirmMessageBox = QMessageBox()
        confirmMessageBox.setText("Are you sure you want to delete this client?")
        confirmMessageBox.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        confirmMessageBox.setDefaultButton(QMessageBox.Cancel)
        result = confirmMessageBox.exec()
        if result == QMessageBox.Ok:
            clients = open("client_ip.txt", "r")
            ips = clients.readlines()
            clients.close()
            for i in range(len(ips)):
                if ips[i].strip() == self.Client_list.currentItem().text().strip():
                    del ips[i]
                    break
            clients = open("client_ip.txt", "w")
            for ip in ips:
                 clients.write(ip)
            clients.close()
            self.listClients()

            

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
