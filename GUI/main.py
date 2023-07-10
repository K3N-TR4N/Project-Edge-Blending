import sys 
import re
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
        
        # Connect buttons on the UI to the corresponding functions
        self.Add_btn.clicked.connect(self.addClient)
        self.Edit_btn.clicked.connect(self.editClient)
        self.Delete_btn.clicked.connect(self.deleteClient)

        # List the clients from the client_ip.txt file
        self.listClients()
        self.Client_list.itemClicked.connect(self.listItemClicked)

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # Fetches the list of clients from client_ip.txt and puts it into the Client_list list widget
    def listClients(self):
        # Clear the list
        self.Client_list.clear()

        # Read all the clients
        with open("client_ip.txt", "r") as clients:
            ips = clients.readlines()
        for ip in ips:
            self.Client_list.addItem(ip.strip())

        # Do some cleanup, disable the edit function as you have to select to do it.
        self.Edit_name.setEnabled(False)
        self.Edit_IP.setEnabled(False)
        self.Edit_btn.setEnabled(False)
        self.Delete_btn.setEnabled(False)
        self.Edit_name.clear()
        self.Edit_IP.clear()
        self.Add_name.clear()
        self.Add_IP.clear()

    # If an item in the list is clicked, allow user to edit and take the information from there into the edit textedits
    def listItemClicked(self):
        self.Edit_name.setEnabled(True)
        self.Edit_IP.setEnabled(True)
        self.Edit_btn.setEnabled(True)
        self.Delete_btn.setEnabled(True)
        self.Edit_name.setText(self.Client_list.currentItem().text().split('-')[0])
        self.Edit_IP.setText(self.Client_list.currentItem().text().split('-')[1])
        
    # This function adds a client to the client_ip.txt file
    def addClient(self):
        # If either the name or IP are blank you are disallowed from adding it.
        if self.Add_name.toPlainText() != "" and self.Add_IP.toPlainText() != "":
            # This regular expression matches with an IPv4 address, any IP added SHOULD be let through.
            if not re.search(r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b", self.Add_IP.toPlainText()):
                # If the IP address is invalid, open an error message informing the user.
                failedMessageBox = QMessageBox()
                failedMessageBox.setText("Enter a valid IP address.")
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return

            # If valid, append the client to the end of client_ip.txt
            with open("client_ip.txt", "a") as clients:
                clients.write("\n" + self.Add_name.toPlainText() + "-" + self.Add_IP.toPlainText())

            # List clients again to refresh
            self.listClients()

    # This function edits an existing line in the client_ip.txt file
    def editClient(self):
        # If either the name or IP are blank you are disallowed from committing that edit.
        if self.Edit_name.toPlainText() != "" and self.Edit_IP.toPlainText() != "":
            # This regular expression matches with an IPv4 address, any IP added SHOULD be let through.
            if not re.search(r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b", self.Edit_IP.toPlainText()):
                failedMessageBox = QMessageBox()
                failedMessageBox.setText("Enter a valid IP address.")
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return

            # Re-open the client_ip.txt file and read the lines
            clients = open("client_ip.txt", "r")
            ips = clients.readlines()
            clients.close()

            # Find the corresponding line in the text file and change it in the list
            for i in range(len(ips)):
                if ips[i].strip() == self.Client_list.currentItem().text().strip():
                    if i == len(ips) - 1:
                        ips[i] = self.Edit_name.toPlainText() + "-" + self.Edit_IP.toPlainText()
                    else:
                        ips[i] = self.Edit_name.toPlainText() + "-" + self.Edit_IP.toPlainText() + "\n"
                    break

            # Re-open the client_ip.txt file for editing and re-write the list
            clients = open("client_ip.txt", "w")
            for ip in ips:
                 clients.write(ip)
            clients.close()

            # List clients again to refresh
            self.listClients()
    
    # This function
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
