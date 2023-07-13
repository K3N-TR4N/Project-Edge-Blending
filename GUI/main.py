import sys 
import re
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
from PyQt5.QtCore import QDataStream, QIODevice

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backend_bases import MouseButton

import matplotlib
import matplotlib.pyplot as plt        
matplotlib.use('Qt5Agg')

import socket
import pickle

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

        self.window_width = 1920
        self.window_height = 1080
        self.boundary_size = 100
        self.boundaries_x = [0, 0, self.window_width, self.window_width, 0]
        self.boundaries_y = [self.window_height, 0, 0, self.window_height, self.window_height]

        self.control_point_1_click_cursor_enable = False
        self.control_point_2_click_cursor_enable = False
        self.control_point_3_click_cursor_enable = False
        self.control_point_4_click_cursor_enable = False

        self.control_point_1_click_count_parity = 0
        self.control_point_2_click_count_parity = 0
        self.control_point_3_click_count_parity = 0
        self.control_point_4_click_count_parity = 0

        self.contrast_curve_click_count_parity = 0
        self.contrast_curve = False

        self.show_areas_click_count_parity = 0
        self.show_areas = False

        self.show_control_points_click_count_parity = 0
        self.show_control_points = False

        #####################################################################

        figure, self.axes = plt.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.control_points_list = {}
        self.bezier_curves = {}

        self.line_area_points = {}
        self.line_area_shapes = {}

        self.client_servers_IP_addresses = {}

        self.PORT = 64012

        plt.connect('button_press_event', self.leftMouseClicked)
        self.horizontalLayout_1.addWidget(self.canvas)

        #'''
        control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
        control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        
        initial_sets_of_control_points = [control_points_1, control_points_2, control_points_3]

        self.index = 0

        for control_points in initial_sets_of_control_points:
            self.index = self.index + 1
            self.control_points_list['Curve ' + str(self.index)] = control_points
            self.bezier_curves['Curve ' + str(self.index)] = PathPatch(Path(control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
            
        for curve in self.bezier_curves:
            self.axes.add_patch(self.bezier_curves[curve])
        #'''

        #####################################################################

        if not self.bezier_curves.keys():
            self.Curve_box.addItem('No Curves')
        else:
            self.Curve_box.addItems(list(self.bezier_curves.keys()))
            
            first_curve_control_points = self.control_points_list[self.Curve_box.currentText()]

            self.control_point_1_x_line.setText(str(first_curve_control_points[0][0]))
            self.control_point_1_y_line.setText(str(first_curve_control_points[0][1]))
            self.control_point_2_x_line.setText(str(first_curve_control_points[1][0]))
            self.control_point_2_y_line.setText(str(first_curve_control_points[1][1]))
            self.control_point_3_x_line.setText(str(first_curve_control_points[2][0]))
            self.control_point_3_y_line.setText(str(first_curve_control_points[2][1]))
            self.control_point_4_x_line.setText(str(first_curve_control_points[3][0]))
            self.control_point_4_y_line.setText(str(first_curve_control_points[3][1]))

            self.redrawCanvas()
        
        self.Curve_box.currentTextChanged.connect(self.selectedCurveChanged)
        self.Client_projectors_box.currentTextChanged.connect(self.clientComboBoxChanged)

        self.Add_curve_btn.clicked.connect(self.addNewCurveClicked)
        self.Remove_curve_btn.clicked.connect(self.removeCurveClicked)
        self.Control_point_1_btn.clicked.connect(self.controlPoint1Clicked)
        self.Control_point_2_btn.clicked.connect(self.controlPoint2Clicked)
        self.Control_point_3_btn.clicked.connect(self.controlPoint3Clicked)
        self.Control_point_4_btn.clicked.connect(self.controlPoint4Clicked)
        self.Set_control_points_btn.clicked.connect(self.setControlPoints)

        self.Left_line_btn.clicked.connect(self.fillLineAreaLeft)
        self.Right_line_btn.clicked.connect(self.fillLineAreaRight)
        self.Above_line_btn.clicked.connect(self.fillLineAreaAbove)
        self.Below_line_btn.clicked.connect(self.fillLineAreaBelow)

        self.Left_line_btn.setEnabled(False)
        self.Right_line_btn.setEnabled(False)
        self.Above_line_btn.setEnabled(False)
        self.Below_line_btn.setEnabled(False)

        self.Show_contrast_curve_btn.clicked.connect(self.contrastCurveClicked)
        self.Show_areas_btn.clicked.connect(self.showAreas)
        self.Show_control_points_btn.clicked.connect(self.showControlPoints)
        
        self.Back_btn.clicked.connect(self.gotoMainWindow)

        self.retrieveProjectors()

    def retrieveProjectors(self):
        client_servers_info_file = open('client_ip.txt', 'r')

        for line in client_servers_info_file:
            client_server_info = str.split(line.removesuffix('\n'), '-')
            self.client_servers_IP_addresses[client_server_info[0]] = client_server_info[1]

        client_servers_info_file.close()

        self.Client_projectors_box.addItems(self.client_servers_IP_addresses.keys())
        
    def redrawCanvas(self):
        self.axes.clear()

        self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')

        if self.Curve_box.currentText() != 'No Curves' and self.show_control_points == True:
            for control_points in self.control_points_list[self.Curve_box.currentText()]:
                self.axes.plot(control_points[0], control_points[1], 'ro')

        for curve in self.bezier_curves:
            if curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.bezier_curves[curve].set(edgecolor = 'r', facecolor = 'r')
            elif curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == False:
                self.bezier_curves[curve].set(edgecolor = 'r', facecolor = 'None')
            elif curve == self.Curve_box.currentText() and self.contrast_curve == False and self.show_areas == True:
                self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'k')
            else:
                if self.show_areas == True:
                    self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'k')
                else:
                    self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'None')
                self.axes.add_patch(self.bezier_curves[curve])

        for area in self.line_area_shapes:
            if area == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.line_area_shapes[area].set(edgecolor = 'r', facecolor = 'r')
            elif area == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == False:
                self.line_area_shapes[area].set(edgecolor = 'r', facecolor = 'None')
            elif area == self.Curve_box.currentText() and self.contrast_curve == False and self.show_areas == True:
                self.line_area_shapes[area].set(edgecolor = 'k', facecolor = 'k')
            else:
                if self.show_areas == True:
                    self.line_area_shapes[area].set(edgecolor = 'k', facecolor = 'k')
                else:
                    self.line_area_shapes[area].set(edgecolor = 'k', facecolor = 'None')
                self.axes.add_patch(self.line_area_shapes[area])

        if self.Curve_box.currentText() in self.bezier_curves:
            self.axes.add_patch(self.bezier_curves[self.Curve_box.currentText()])
        if self.Curve_box.currentText() in self.line_area_shapes.keys():
            self.axes.add_patch(self.line_area_shapes[self.Curve_box.currentText()])

        self.axes.set_xlim((0 - self.boundary_size * 3, self.window_width + self.boundary_size * 3))
        self.axes.set_ylim((0 - self.boundary_size * 3, self.window_height + self.boundary_size * 3))
        self.axes.grid(color = 'k')
        self.canvas.draw() 

    def setControlPoints(self):      
        if self.Curve_box.currentText() == 'No Curves':
            return
        else:
            
            if self.evaluateLineEditFields() == 'Valid':
                user_control_point_1_x = float(self.control_point_1_x_line.text())
                user_control_point_2_x = float(self.control_point_2_x_line.text())
                user_control_point_3_x = float(self.control_point_3_x_line.text())
                user_control_point_4_x = float(self.control_point_4_x_line.text())
                user_control_point_1_y = float(self.control_point_1_y_line.text())
                user_control_point_2_y = float(self.control_point_2_y_line.text())
                user_control_point_3_y = float(self.control_point_3_y_line.text())
                user_control_point_4_y = float(self.control_point_4_y_line.text())
            else: 
                return
            
            user_control_point_values = [user_control_point_1_x, user_control_point_1_y, 
                                            user_control_point_2_x, user_control_point_2_y, 
                                            user_control_point_3_x, user_control_point_3_y, 
                                            user_control_point_4_x, user_control_point_4_y]

            if self.evaluateControlPoints(user_control_point_values = user_control_point_values) == 'Invalid':
                return

            new_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]
            self.control_points_list[self.Curve_box.currentText()] = new_control_points
            self.bezier_curves[self.Curve_box.currentText()] = PathPatch(Path(new_control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)

            if self.Curve_box.currentText() in self.line_area_shapes:
                del self.line_area_shapes[self.Curve_box.currentText()]

            self.redrawCanvas()
            self.SendInfo()
            
            self.evaluateLineCurve(line_name = self.Curve_box.currentText(), new_control_points = new_control_points)
        
    def addNewCurveClicked(self):

        if self.evaluateLineEditFields() == 'Valid':
            user_control_point_1_x = float(self.control_point_1_x_line.text())
            user_control_point_2_x = float(self.control_point_2_x_line.text())
            user_control_point_3_x = float(self.control_point_3_x_line.text())
            user_control_point_4_x = float(self.control_point_4_x_line.text())
            user_control_point_1_y = float(self.control_point_1_y_line.text())
            user_control_point_2_y = float(self.control_point_2_y_line.text())
            user_control_point_3_y = float(self.control_point_3_y_line.text())
            user_control_point_4_y = float(self.control_point_4_y_line.text())
        else: 
            return
        
        user_control_point_values = [user_control_point_1_x, user_control_point_1_y, 
                                        user_control_point_2_x, user_control_point_2_y, 
                                        user_control_point_3_x, user_control_point_3_y, 
                                        user_control_point_4_x, user_control_point_4_y]

        if self.evaluateControlPoints(user_control_point_values = user_control_point_values) == 'Invalid':
            return

        new_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]

        new_bezier_curve = PathPatch(Path(new_control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none')
        
        new_bezier_curve_name = 'Curve ' + str(len(self.control_points_list) + 1)
        self.control_points_list[new_bezier_curve_name] = new_control_points
        self.bezier_curves[new_bezier_curve_name] = new_bezier_curve

        self.Curve_box.addItem(new_bezier_curve_name)
        self.axes.add_patch(new_bezier_curve)
        self.canvas.draw()

        if self.Curve_box.currentText() == 'No Curves':
            self.Curve_box.removeItem(self.Curve_box.currentIndex())
        else:
            self.Curve_box.setCurrentText('Curve ' + str(len(self.control_points_list)))

        self.evaluateLineCurve(line_name = new_bezier_curve_name, new_control_points = new_control_points)

    def evaluateLineEditFields(self):

        user_control_point_values = [self.control_point_1_x_line.text(), self.control_point_2_x_line.text(), 
                                     self.control_point_3_x_line.text(), self.control_point_4_x_line.text(), 
                                     self.control_point_1_y_line.text(), self.control_point_2_y_line.text(), 
                                     self.control_point_3_y_line.text(), self.control_point_4_y_line.text()]

        for control_point_value in user_control_point_values:
            if re.fullmatch("[-]?[0-9]+[.]?[0-9]*", str(control_point_value)) == None:
                print('Invalid control point values! Values for control points cannot include letters, symbols, or spaces.')
                return 'Invalid'

        return 'Valid'

    #   All four control points cannot have the same coordinate
    #   Control Point 1 and Control 4 cannot be at the same point
    #   Control Point 1 and Control 4 have to be on the boundary lines
    def evaluateControlPoints(self, user_control_point_values):    
        if len(set(user_control_point_values)) == 1:
            print('Invalid control points! All four control points cannot be on the same coordinate.')
            return 'Invalid'
        if user_control_point_values[0] == user_control_point_values[6] and user_control_point_values[1] == user_control_point_values[7]:
            print('Invalid control points! Control point 1 and control point 4 cannot be the same if control point 2 and control point 3 are the same.')
            return 'Invalid'
        if user_control_point_values[0] < 0 or user_control_point_values[0] > self.window_width or user_control_point_values[1] < 0 or user_control_point_values[1] > self.window_height:
            print('Invalid control points! Control point 1 must be on the blue dashed lines.')
            return 'Invalid'
        else:
            if user_control_point_values[1] != 0 and user_control_point_values[1] != self.window_height and user_control_point_values[0] != 0 and user_control_point_values[0] != self.window_width:
                print('Invalid control points! Control point 1 must be on the blue dashed lines.')
                return 'Invalid'

        if user_control_point_values[6] < 0 or user_control_point_values[6] > self.window_width or user_control_point_values[7] < 0 or user_control_point_values[7] > self.window_height:
            print('Invalid control points! Control point 4 must be on the blue dashed lines.')
            return 'Invalid'
        else:
            if user_control_point_values[7] != 0 and user_control_point_values[7] != self.window_height and user_control_point_values[6] != 0 and user_control_point_values[6] != self.window_width:
                print('Invalid control points! Control point 4 must be on the blue dashed lines.')
                return 'Invalid'
        
        return 'Valid'
    
    def evaluateLineCurve(self, line_name, new_control_points):

        if len(set(new_control_points)) == 2:
            self.Add_curve_btn.setEnabled(False)
            self.Remove_curve_btn.setEnabled(False)

            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            
            self.Set_control_points_btn.setEnabled(False)

            self.Curve_box.setEnabled(False)

            self.line_control_point_name = line_name
            self.line_control_point_1 = new_control_points[0]
            self.line_control_point_4 = new_control_points[3]

            if self.line_control_point_1[1] == self.line_control_point_4[1]:

                if (self.line_control_point_1[0] == 0.0 and self.line_control_point_4[0] == self.window_width) or (self.line_control_point_1[0] == self.window_width and self.line_control_point_4[0] == 0):
                    self.Left_line_btn.setEnabled(False)
                    self.Right_line_btn.setEnabled(False)
                    self.Above_line_btn.setEnabled(True)
                    self.Below_line_btn.setEnabled(True)
                else:
                    print('Invalid control points! For horizontal lines, control points 1 and 4 must be on the ends of the projection screen.')
                    
                    self.Add_curve_btn.setEnabled(True)
                    self.Remove_curve_btn.setEnabled(True)

                    self.Control_point_1_btn.setEnabled(True)
                    self.Control_point_2_btn.setEnabled(True)
                    self.Control_point_3_btn.setEnabled(True)
                    self.Control_point_4_btn.setEnabled(True)

                    self.Set_control_points_btn.setEnabled(True)

                    self.Curve_box.setEnabled(True)
                    
                    return
            
            else:
                self.Left_line_btn.setEnabled(True)
                self.Right_line_btn.setEnabled(True)
                self.Above_line_btn.setEnabled(False)
                self.Below_line_btn.setEnabled(False)

    
    def fillLineAreaLeft(self):
        if self.line_control_point_1[1] == 0:                
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, float(self.window_height))]
        else:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, float(self.window_height))]
        self.makeFillArea(control_points_line_area)
            
    def fillLineAreaRight(self):
        if self.line_control_point_1[1] == 0:
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (float(self.window_width), 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), float(self.window_height))]
        else:
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (float(self.window_width), 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), float(self.window_height))]
        self.makeFillArea(control_points_line_area)

    def fillLineAreaAbove(self):
        if self.line_control_point_1[0] == 0:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), float(self.window_height)),
                                        (0.0, float(self.window_height))]
        else:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), float(self.window_height)),
                                        (0.0, float(self.window_height))]
        self.makeFillArea(control_points_line_area)

    def fillLineAreaBelow(self):
        if self.line_control_point_1[0] == 0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), 0.0),
                                        (0.0, 0.0)]
        else:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), 0.0),
                                        (0.0, 0.0)]
        self.makeFillArea(control_points_line_area)
            
    def makeFillArea(self, control_points_line_area):
                
            self.Left_line_btn.setEnabled(False)
            self.Right_line_btn.setEnabled(False)
            self.Above_line_btn.setEnabled(False)
            self.Below_line_btn.setEnabled(False)

            self.line_area_points[self.line_control_point_name] = control_points_line_area
            self.line_area_shapes[self.line_control_point_name] = PathPatch(Path(control_points_line_area, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = 'r', transform=self.axes.transData)

            self.redrawCanvas()

            self.Add_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)

            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)

            self.Set_control_points_btn.setEnabled(True)

            self.Curve_box.setEnabled(True)

    def removeCurveClicked(self):

        if self.Curve_box.currentText() == 'No Curves':
            return
        else:
            
            removed_curve_number = int(str.split(self.Curve_box.currentText(), ' ')[1])
            total_curves_before_removal = len(self.bezier_curves)

            if removed_curve_number < total_curves_before_removal:
                changed_curves = []
                index = removed_curve_number + 1

                while index <= total_curves_before_removal:
                    changed_curves.append('Curve ' + str(index))
                    index = index + 1
            
                for changed_curve in changed_curves:
                    new_curve_number = int(str.split(changed_curve, ' ')[1]) - 1
                    
                    self.control_points_list['Curve ' + str(new_curve_number)] = self.control_points_list[changed_curve]
                    del self.control_points_list[changed_curve]

                    self.bezier_curves['Curve ' + str(new_curve_number)] = self.bezier_curves[changed_curve]
                    del self.bezier_curves[changed_curve]
                    
                    if changed_curve in self.line_area_shapes:
                        self.line_area_shapes['Curve ' + str(new_curve_number)] = self.line_area_shapes[changed_curve]
                        del self.line_area_shapes[changed_curve]

                self.Curve_box.clear()
                self.Curve_box.addItems(list(self.bezier_curves.keys()))

            else:
                del self.control_points_list[self.Curve_box.currentText()]
                del self.bezier_curves[self.Curve_box.currentText()]
        
                if self.Curve_box.currentText() in self.line_area_shapes:
                    del self.line_area_shapes[self.Curve_box.currentText()]

                if not self.bezier_curves.keys():
                    self.Curve_box.addItem('No Curves')

                self.Curve_box.removeItem(self.Curve_box.currentIndex())

            self.redrawCanvas()


    def selectedCurveChanged(self):
        
        if self.Curve_box.currentText() == 'No Curves' or self.Curve_box.currentText() == '':
            return
        else:
            selected_curve_control_points = self.control_points_list[self.Curve_box.currentText()]

            self.control_point_1_x_line.setText(str(selected_curve_control_points[0][0]))
            self.control_point_1_y_line.setText(str(selected_curve_control_points[0][1]))
            self.control_point_2_x_line.setText(str(selected_curve_control_points[1][0]))
            self.control_point_2_y_line.setText(str(selected_curve_control_points[1][1]))
            self.control_point_3_x_line.setText(str(selected_curve_control_points[2][0]))
            self.control_point_3_y_line.setText(str(selected_curve_control_points[2][1]))
            self.control_point_4_x_line.setText(str(selected_curve_control_points[3][0]))
            self.control_point_4_y_line.setText(str(selected_curve_control_points[3][1]))

            self.redrawCanvas()        


    def controlPoint1Clicked(self):
        
        self.control_point_1_click_count_parity = self.control_point_1_click_count_parity + 1

        if self.control_point_1_click_count_parity % 2 == 0:            
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)
            self.control_point_1_click_cursor_enable = False
            self.control_point_1_click_count_parity == 0
        else:
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_1_click_cursor_enable = True
    
    def controlPoint2Clicked(self):

        self.control_point_2_click_count_parity = self.control_point_2_click_count_parity + 1

        if self.control_point_2_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)
            self.control_point_2_click_cursor_enable = False
            self.control_point_2_click_count_parity == 0
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_2_click_cursor_enable = True

    def controlPoint3Clicked(self):

        self.control_point_3_click_count_parity = self.control_point_3_click_count_parity + 1

        if self.control_point_3_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)        
            self.control_point_3_click_cursor_enable = False
            self.control_point_3_click_count_parity == 0
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_3_click_cursor_enable = True
    
    def controlPoint4Clicked(self):

        self.control_point_4_click_count_parity = self.control_point_4_click_count_parity + 1

        if self.control_point_4_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)        
            self.control_point_4_click_cursor_enable = False
            self.control_point_4_click_count_parity == 0
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.control_point_4_click_cursor_enable = True

    def contrastCurveClicked(self):

        self.contrast_curve_click_count_parity = self.contrast_curve_click_count_parity + 1

        if self.contrast_curve_click_count_parity % 2 == 0:
            self.contrast_curve = False
            self.contrast_curve_click_count_parity =0
        else:
            self.contrast_curve = True

        self.redrawCanvas()

    def showAreas(self):

        self.show_areas_click_count_parity = self.show_areas_click_count_parity + 1

        if self.show_areas_click_count_parity % 2 == 0:
            self.show_areas = False
            self.show_areas_click_count_parity = 0
        else:
            self.show_areas = True
        self.redrawCanvas()

    def showControlPoints(self):

        self.show_control_points_click_count_parity = self.show_control_points_click_count_parity + 1

        if self.show_control_points_click_count_parity % 2 == 0:
            self.show_control_points = False
            self.show_control_points_click_count_parity = 0
        else:
            self.show_control_points = True
        self.redrawCanvas()

    def leftMouseClicked(self, event):
        if event.button == MouseButton.LEFT:
            if self.control_point_1_click_cursor_enable:
                if event.xdata != None and event.ydata != None:
                    self.control_point_1_x_line.setText(str(round(event.xdata, 2)))
                    self.control_point_1_y_line.setText(str(round(event.ydata, 2)))
                    self.setControlPoints()

            elif self.control_point_2_click_cursor_enable:
                if event.xdata != None and event.ydata != None:
                    self.control_point_2_x_line.setText(str(round(event.xdata, 2)))
                    self.control_point_2_y_line.setText(str(round(event.ydata, 2)))
                    self.setControlPoints()

            elif self.control_point_3_click_cursor_enable:
                if event.xdata != None and event.ydata != None:
                    self.control_point_3_x_line.setText(str(round(event.xdata, 2)))
                    self.control_point_3_y_line.setText(str(round(event.ydata, 2)))
                    self.setControlPoints()
            
            elif self.control_point_4_click_cursor_enable:
                if event.xdata != None and event.ydata != None:
                    self.control_point_4_x_line.setText(str(round(event.xdata, 2)))
                    self.control_point_4_y_line.setText(str(round(event.ydata, 2)))
                    self.setControlPoints()

    ###########################################################
    # NETWORKING
    ###########################################################

    def clientComboBoxChanged(self):
        #self.GetInfo()
        test = 1

    def GetInfo(self):
        clientIP = self.client_servers_IP_addresses[self.Client_projectors_box.currentText()]
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(clientIP, self.PORT, QIODevice.ReadWrite)
        self.tcpSocket.waitForConnected(1000)
        toSend = "send"
        toSend = pickle.dumps(toSend, -1)
        self.tcpSocket.write(toSend)
        self.tcpSocket.waitForReadyRead()


    def SendInfo(self):
        clientIP = self.client_servers_IP_addresses[self.Client_projectors_box.currentText()]
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(clientIP, self.PORT, QIODevice.ReadWrite)
        self.tcpSocket.waitForConnected(10000)
        toSend = [self.control_points_list, self.line_area_points]
        toSend = pickle.dumps(toSend, -1)
        self.tcpSocket.write(toSend)
        self.tcpSocket.waitForReadyRead()
        print(pickle.loads(self.tcpSocket.readAll()))

    def gotoMainWindow(self):
        mainWindow = MainWindow()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)


###################################################
# PROJECTOR CONFIGURATION
###################################################
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
    #widget.setFixedHeight(600)
    #widget.setFixedWidth(900)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
