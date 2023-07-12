import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QEvent, QObject
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.path import Path
from matplotlib.patches import PathPatch

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Image Window")

        figure, self.axes = plt.subplots()
        self.axes.clear()

        self.control_points_list = []
        self.bezier_curves = {}

        self.line_area_points = []
        self.line_area_shapes = {}

        self.window_width = 2560
        self.window_height = 1440
        self.axes.set_xlim([0, self.window_width])
        self.axes.set_ylim([0, self.window_height])


        control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
        control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        
        self.control_points_list = [control_points_1, control_points_2, control_points_3]
        self.line_area_points = [[(0.0, float(self.window_height)), 
                                        (0.0, 0.0), 
                                        (0.0, 0.0), 
                                        (float(self.window_width), float(self.window_height)), 
                                        (0.0, float(self.window_height))]]
        ###
        # DO NETWORKING
        ###
        print(self.control_points_list)
        #curve1 = PathPatch(Path(control_points_1, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = 'k', edgecolor = 'k', transform = self.axes.transData)
        #self.axes.add_patch(curve1)
        
        
        for curve in self.control_points_list:
            bezierCurve = PathPatch(Path(curve, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), facecolor = 'k', edgecolor = 'k', transform = self.axes.transData)
            self.axes.add_patch(bezierCurve)
            print(curve)

        for area in self.line_area_points:
            bezierArea = PathPatch(Path(area, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = 'k', edgecolor = 'k', transform=self.axes.transData)
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
        figure.set_size_inches(25.6, 14.4)

        # save output as transparent
        figure.tight_layout(pad=0)
        plt.savefig('figure.png', transparent = True, dpi=100)

        # Load the image
        self.image_path = "figure.png"
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
    window.showFullScreen()
    # Start the event loop
    sys.exit(app.exec())