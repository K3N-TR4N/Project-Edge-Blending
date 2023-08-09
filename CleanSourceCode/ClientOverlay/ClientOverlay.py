import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtNetwork import QHostAddress, QTcpServer

import matplotlib.pyplot as plt 
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import pickle
from win32api import GetSystemMetrics

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        

        # Set window title
        self.setWindowTitle("Image Window")

        # Sets up initial figure using matplotlib
        self.figure, self.axes = plt.subplots()
        self.axes.clear()

        ## Dictionary containing the control points used for bezier curves.
        # The exact format of the control_points_list is {"Curve number" : [[control points], opacity]}.
        # Curve number is the associated number of the curve. 
        # [control points] is an array containing all the control points for the curve. 
        # opacity is a value from 0 to 1 containing the opacity value used for drawing the area of the curve.
        self.control_points_list = {}

        ## Dictionary containing generated bezier curves based on the control points.
        self.bezier_curves = {}

        ## Dictionary containing "line" type bezier curves.
        # Lines are defined as bezier curves with only two unique control points. The other two control points have equal coordinates to either of the unique control points.
        # The reason lines are defined separately from normal bezier curves is due to the way we draw areas pertaining to lines, which has to be done more manually.
        self.line_area_points = {}

        ## Dictionary containing the shapes for areas under lines.
        self.line_area_shapes = {}

        ## Width of the main display in pixels.
        self.window_width = GetSystemMetrics(0)

        ## Height of the main display in pixels.
        self.window_height = GetSystemMetrics(1)

        # Sets the x and y width and height to the width and height of the main display.
        self.axes.set_xlim([0, self.window_width])
        self.axes.set_ylim([0, self.window_height])

        ## Port number used for incoming TCP Connections over the local network.
        self.PORT = 64012

        ## Filename of the file containing bezier information saved on the local computer.
        # bezierinfo contains the control_points_list and line_area_points dictionaries in byte format.
        self.fileName = "bezierInfo"

        # Using a try statement, we attempt to open the bezierinfo file. If no file is found, then no information is saved.
        try:
            f = open(self.fileName, "rb")
            textFromFile = f.read()
            asArray = pickle.loads(textFromFile)
            self.control_points_list = asArray[0]
            self.line_area_points = asArray[1]
            f.close()
        except FileNotFoundError:
            print("no file")

        # Iterating over the control_points_list dictionary, we get all the bezier curves in the bezierinfo file and apply them.
        for curveName, value in self.control_points_list.items():
            # If a bezier curve is in the line dictionary, it doesn't need to be drawn here.
            if curveName in self.line_area_points.keys():
                continue
            # Retrieve the opacity from the dictionary and make an RGB color of black with that opacity.
            opacity = (0, 0, 0, value[1])
            # Set the bezier curve, setting the facecolor to the opacity value
            bezierCurve = PathPatch(Path(value[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = opacity, edgecolor = "none", transform = self.axes.transData)
            # Add the bezier curve to the patches.
            self.axes.add_patch(bezierCurve)
        
        # In the same way as the control points list dictionary, we iterate over the line area points dictionary and apply the same principles to the lines.
        for areaName, value in self.line_area_points.items():
            opacity = (0, 0, 0, value[1])
            bezierArea = PathPatch(Path(value[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = opacity, edgecolor = "none", transform=self.axes.transData)
            self.axes.add_patch(bezierArea)

        # The next sequence of code makes the image used for the overlay.
        # Make the spines of the axes not visible.
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)

        # Remove the axis ticks and labels
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])

        # Set the figure size to the main display's width and height.
        self.figure.set_size_inches(self.window_width / 100.0, self.window_height / 100.0)

        # save output as transparent
        self.figure.tight_layout(pad=0)
        plt.savefig('figure.png', transparent = True, dpi=100)

        # Load the image
        ## Path used for the image for the overlay
        # Set to "figure.png"
        self.image_path = "figure.png"

        ## QLabel used to display the image.
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(self.image_path))

        # Set the image label as the central widget
        self.setCentralWidget(self.image_label)

        ## TCP Server used for accepting incoming connections.
        self.tcpServer = QTcpServer(self)
        HOST = QHostAddress("0.0.0.0")

        # If any new connections are detected, go to the incomingConnection function.
        self.tcpServer.newConnection.connect(self.incomingConnection)
        if not self.tcpServer.listen(HOST, self.PORT):
            print("none")
        
    ## This function handles all incoming connections over the given port number on the local network.
    def incomingConnection(self):
        ## QTcpSocket connection made with the host computer.
        self.clientConnection = self.tcpServer.nextPendingConnection()        
        self.clientConnection.waitForReadyRead()
        
        ## Incoming QByteArray from the host computer
        # Will either contain the word "send", in which case the client will send bezier info to the host, or will contain new bezier info to apply.
        self.received = self.clientConnection.readAll()
        self.received = pickle.loads(self.received)
        
        self.clientConnection.disconnected.connect(self.clientConnection.deleteLater)
        
        
        if str(self.received).strip() == "send":
            # Sends the current bezier info that is saved to the host.
            sendArray = [self.control_points_list, self.line_area_points, self.window_width, self.window_height]
            self.clientConnection.write(pickle.dumps(sendArray, -1))
        else:
            # Receives bezier information from the host and formulates the new bezier curves.
            self.control_points_list = self.received[0]
            self.line_area_points = self.received[1]
            self.clientConnection.write(pickle.dumps("received info", -1))
            
            # Resets the axes.
            self.axes.clear()
            self.axes.set_xlim([0, self.window_width])
            self.axes.set_ylim([0, self.window_height])

            # Iterate through the control_points_list and makes the new curves.
            for curveName, value in self.control_points_list.items():
                if curveName in self.line_area_points.keys():
                    continue
                opacity = (0, 0, 0, value[1])
                bezierCurve = PathPatch(Path(value[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = opacity, edgecolor = "none", transform = self.axes.transData)
                self.axes.add_patch(bezierCurve)
            
            # Iterate through the line_area_points list and makes the new lines.
            for areaName, value in self.line_area_points.items():
                opacity = (0, 0, 0, value[1])
                bezierArea = PathPatch(Path(value[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = opacity, edgecolor = "none", transform=self.axes.transData)
                self.axes.add_patch(bezierArea)

            
            # The next sequence of code makes the image used for the overlay.
            # Make the spines of the axes not visible.
            self.axes.spines['top'].set_visible(False)
            self.axes.spines['right'].set_visible(False)
            self.axes.spines['bottom'].set_visible(False)
            self.axes.spines['left'].set_visible(False)

            # Remove the axis ticks and labels
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.axes.set_xticklabels([])
            self.axes.set_yticklabels([])

            # Set the figure size to 1920x1080 pixels
            self.figure.set_size_inches(self.window_width / 100.0, self.window_height / 100)

            # save output as transparent
            plt.savefig('figure.png', transparent = True, dpi=100)

            # Load the image
            self.image_path = "figure.png"
            self.image_label = QLabel(self)
            self.image_label.setPixmap(QPixmap(self.image_path))

            # Set the image label as the central widget
            self.setCentralWidget(self.image_label)

            # Open the bezierinfo file to write the new bezier information to, in the format of an array of the control_points_list and the line_area_points dictionaries.
            f = open(self.fileName, "wb")
            array = [self.control_points_list, self.line_area_points]
            f.write(pickle.dumps(array, -1))
            f.close()
        


if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = ImageWindow()

    # Produces a borderless window that is always on top.
    window.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
    #window.setWindowFlags(Qt.FramelessWindowHint)

    # This indicates that the widget should have a translucent background
    window.setAttribute(Qt.WA_TranslucentBackground)

    # Maximizes the window 
    window.showFullScreen()
    # Start the event loop
    sys.exit(app.exec())