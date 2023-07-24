from array import array
import fileinput
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import socket
import pickle
from win32api import GetSystemMetrics

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        

        # Set window title
        self.setWindowTitle("Image Window")

        self.figure, self.axes = plt.subplots()
        self.axes.clear()

        self.control_points_list = {}
        self.bezier_curves = {}

        self.line_area_points = {}
        self.line_area_shapes = {}

        self.window_width = GetSystemMetrics(0)
        self.window_height = GetSystemMetrics(1)
        self.axes.set_xlim([0, self.window_width])
        self.axes.set_ylim([0, self.window_height])
#test
        self.PORT = 64012
        self.fileName = "bezierInfo"
        try:
            f = open(self.fileName, "rb")
            textFromFile = f.read()
            asArray = pickle.loads(textFromFile)
            self.control_points_list = asArray[0]
            self.line_area_points = asArray[1]
            f.close()
        except FileNotFoundError:
            print("no file")

        
        '''
        control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
        control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        
        self.control_points_list = [control_points_1, control_points_2, control_points_3]
        self.line_area_points = [[(0.0, float(self.window_height)), 
                                        (0.0, 0.0), 
                                        (0.0, 0.0), 
                                        (float(self.window_width), float(self.window_height)), 
                                        (0.0, float(self.window_height))]]
        '''

        for curveName, value in self.control_points_list.items():
            opacity = (0, 0, 0, value[1])
            bezierCurve = PathPatch(Path(value[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = opacity, edgecolor = opacity, transform = self.axes.transData)
            self.axes.add_patch(bezierCurve)

        for areaName, value in self.line_area_points.items():
            opacity = (0, 0, 0, value[1])
            bezierArea = PathPatch(Path(value[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = opacity, edgecolor = opacity, transform=self.axes.transData)
            self.axes.add_patch(bezierArea)
        #plt.show()

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
        self.figure.set_size_inches(self.window_width / 100.0, self.window_height / 100.0)

        # save output as transparent
        self.figure.tight_layout(pad=0)
        plt.savefig('figure.png', transparent = True, dpi=100)

        #Load the image
        self.image_path = "figure.png"
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(self.image_path))

        # Set the image label as the central widget
        self.setCentralWidget(self.image_label)

        

        self.tcpServer = QTcpServer(self)
        HOST = QHostAddress("0.0.0.0")
        self.tcpServer.newConnection.connect(self.incomingConnection)
        if not self.tcpServer.listen(HOST, self.PORT):
            print("none")
        

    def incomingConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()        

        clientConnection.waitForReadyRead()
        
        
        received = clientConnection.readAll()
        received = pickle.loads(received)
        
        clientConnection.disconnected.connect(clientConnection.deleteLater)
        
        
        if str(received).strip() == "send":
            #send data
            sendArray = [self.control_points_list, self.line_area_points, self.window_width, self.window_height]
            clientConnection.write(pickle.dumps(sendArray, -1))
            send = 0
        else:
            #set curves
            print(received)
            self.control_points_list = received[0]
            self.line_area_points = received[1]
            clientConnection.write(pickle.dumps("received info", -1))
        
            self.axes.clear()
            self.axes.set_xlim([0, self.window_width])
            self.axes.set_ylim([0, self.window_height])
            for curveName, value in self.control_points_list.items():
                opacity = (0, 0, 0, value[1])
                bezierCurve = PathPatch(Path(value[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = opacity, edgecolor = (0, 0, 0, 0.01), transform = self.axes.transData)
                self.axes.add_patch(bezierCurve)

            for areaName, value in self.line_area_points.items():
                opacity = (0, 0, 0, value[1])
                bezierArea = PathPatch(Path(value[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = opacity, edgecolor = (0, 0, 0, 0.01), transform=self.axes.transData)
                self.axes.add_patch(bezierArea)

            
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

            #Load the image
            self.image_path = "figure.png"
            self.image_label = QLabel(self)
            self.image_label.setPixmap(QPixmap(self.image_path))

            # Set the image label as the central widget
            self.setCentralWidget(self.image_label)

            f = open(self.fileName, "wb")
            array = [self.control_points_list, self.line_area_points]
            f.write(pickle.dumps(array, -1))
            f.close()
        


if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = ImageWindow()

    # Produces a borderless window
    window.setWindowFlags(Qt.FramelessWindowHint)
    #window.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

    # This indicates that the widget should have a translucent background
    window.setAttribute(Qt.WA_TranslucentBackground)

    # Maximizes the window 
    window.showFullScreen()
    # Start the event loop
    sys.exit(app.exec())