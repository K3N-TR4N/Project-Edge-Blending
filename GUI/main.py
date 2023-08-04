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

import pickle

# This file contains all the functionalities of the widgets between the windows

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("MainWindow.ui", self)
        widget.setWindowTitle('Planetarium Edge Blend')
        self.GeometryEdit_btn.clicked.connect(self.gotoMaskFeedAndGeometryEditingWindow)
        self.ProjectorConfig_btn.clicked.connect(self.gotoProjectorConfigurationWindow)

    def gotoMaskFeedAndGeometryEditingWindow(self):
        geometryEdit = MaskFeedAndGeometryEditingWindow()
        widget.setWindowTitle('Mask Feed and Geometry Editing - Planetarium Edge Blend')
        widget.addWidget(geometryEdit)
        widget.setCurrentIndex(widget.currentIndex() + 1)
#test
    def gotoProjectorConfigurationWindow(self):
        projectorConfig = ProjectorConfigurationWindow()
        widget.setWindowTitle('Projector Configuration - Planetarium Edge Blend')
        widget.addWidget(projectorConfig)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class MaskFeedAndGeometryEditingWindow(QMainWindow):
    def __init__(self):
        super(MaskFeedAndGeometryEditingWindow, self).__init__()
        loadUi("MaskFeedAndGeometryEditingWindow.ui", self)

        self.window_width = 1280
        self.window_height = 720
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

        self.line_mode_click_count_parity = 0
        self.line_mode_on = False

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
        self.retrieveProjectors()

        plt.connect('button_press_event', self.leftMouseClicked)
        self.horizontalLayout_1.addWidget(self.canvas)
        try:
            self.GetInfo()
            if (self.control_points_list or self.line_area_points):
                for pointName, pointValue in self.control_points_list.items():
                    self.bezier_curves[pointName] = PathPatch(Path(pointValue[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
            
                for curve in self.bezier_curves:
                    self.axes.add_patch(self.bezier_curves[curve])

                for lineName, lineValue in self.line_area_points.items():
                    self.line_area_shapes[lineName] = PathPatch(Path(lineValue[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = 'none', transform=self.axes.transData)

                for line in self.line_area_shapes:
                    self.axes.add_patch(self.line_area_shapes[line])

                selected_curve_opacity_alpha_value = self.control_points_list["Curve 1"][1]
                self.Curve_opacity_box.setValue(selected_curve_opacity_alpha_value * 100)

            self.axes.set_title(self.Client_projectors_box.currentText() + ' Mask')
            self.axes.set_xlabel('Screen Width')
            self.axes.set_ylabel('Screen Height')
            self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')
            self.axes.set_xlim((0 - self.boundary_size * 3, self.window_width + self.boundary_size * 3))
            self.axes.set_ylim((0 - self.boundary_size * 3, self.window_height + self.boundary_size * 3))

            '''
            else:
                
                control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
                control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
                control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
            
                initial_sets_of_control_points = [control_points_1, control_points_2, control_points_3]

                self.index = 0

                for control_points in initial_sets_of_control_points:
                    self.index = self.index + 1
                    self.control_points_list['Curve ' + str(self.index)] = [control_points, 1.0]
                    self.bezier_curves['Curve ' + str(self.index)] = PathPatch(Path(control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
                
                for curve in self.bezier_curves:
                    self.axes.add_patch(self.bezier_curves[curve])
                self.SendInfo()
                '''
            
        except:
            self.Line_mode_btn.setEnabled(False)
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.Set_curve_btn.setEnabled(False)
            self.Add_curve_btn.setEnabled(False)
            self.Remove_curve_btn.setEnabled(False)
            self.Show_contrast_curve_btn.setEnabled(False)
            self.Show_areas_btn.setEnabled(False)
            self.Show_control_points_btn.setEnabled(False)

            errorBox = QMessageBox()
            errorBox.setWindowTitle('Connection Error - Planetarium Edge Blend')
            errorBox.setText("Client at IP Address not found. Are you sure the client application is running on it?")
            errorBox.exec()

            self.axes.set_title('Not connected to ' + self.Client_projectors_box.currentText())

        self.axes.grid(color = 'k')
        self.canvas.draw()   

        #####################################################################

        self.setTextBoxes()
        
        self.Curve_box.currentTextChanged.connect(self.selectedCurveChanged)
        self.Client_projectors_box.currentTextChanged.connect(self.clientComboBoxChanged)

        self.Add_curve_btn.clicked.connect(self.addNewCurveClicked)
        self.Remove_curve_btn.clicked.connect(self.removeCurveClicked)
        self.Control_point_1_btn.clicked.connect(self.controlPoint1Clicked)
        self.Control_point_2_btn.clicked.connect(self.controlPoint2Clicked)
        self.Control_point_3_btn.clicked.connect(self.controlPoint3Clicked)
        self.Control_point_4_btn.clicked.connect(self.controlPoint4Clicked)
        self.Set_curve_btn.clicked.connect(self.setCurve)
        
        self.Line_mode_btn.clicked.connect(self.lineModeClicked)
        self.control_point_1_x_line.textChanged.connect(self.controlPoint1XChanged)
        self.control_point_1_y_line.textChanged.connect(self.controlPoint1YChanged)

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

    def setTextBoxes(self):
        if not self.bezier_curves.keys():
            self.Curve_box.addItem('No Curves')

            self.Set_curve_btn.setEnabled(False)
            self.Remove_curve_btn.setEnabled(False)
        else:
            self.Curve_box.clear()
            self.Curve_box.addItems(list(self.bezier_curves.keys()))
            
            first_curve_control_points = self.control_points_list[self.Curve_box.currentText()][0]

            self.control_point_1_x_line.setText(str(first_curve_control_points[0][0]))
            self.control_point_1_y_line.setText(str(first_curve_control_points[0][1]))
            self.control_point_2_x_line.setText(str(first_curve_control_points[1][0]))
            self.control_point_2_y_line.setText(str(first_curve_control_points[1][1]))
            self.control_point_3_x_line.setText(str(first_curve_control_points[2][0]))
            self.control_point_3_y_line.setText(str(first_curve_control_points[2][1]))
            self.control_point_4_x_line.setText(str(first_curve_control_points[3][0]))
            self.control_point_4_y_line.setText(str(first_curve_control_points[3][1]))

            self.redrawCanvas()

    ## Retrieves all configured projectors' names and IP addresses.
    # Reads a text file on the host computer containing all of the configured projectors' information and stores that information into a dictionary.
    def retrieveProjectors(self):
        client_servers_info_file = open('client_ip.txt', 'r')

        # Reads each line from the text line and removes the newline character before creating a key value pair in the client_servers_IP_addresses dictionary.
        for line in client_servers_info_file:
            client_server_info = str.split(line.removesuffix('\n'), '-')
            self.client_servers_IP_addresses[client_server_info[0]] = client_server_info[1]

        client_servers_info_file.close()

        # Updates the combo box so that the user can now select each of the configured projectors to view and edit a client projector mask.
        self.Client_projectors_box.addItems(self.client_servers_IP_addresses.keys())
        
    ## Clears the mask graph containing all of Bezier curves for a client projector mask and plots each Bezier curve again.
    def redrawCanvas(self):
        self.axes.clear()

        self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')

        # If the user has clicked on the 'Show Control Points' button, then the control points for a selected Bezier curve will be plotted in red on the mask graph.
        if self.Curve_box.currentText() != 'No Curves' and self.show_control_points == True:
            for control_points in self.control_points_list[self.Curve_box.currentText()][0]:
                self.axes.plot(control_points[0], control_points[1], 'ro')

        # Iterates through each Bezier curve that the user has created and will evaluate each Bezier curve for a set of conditions before plotting them onto the graph.
        for curve in self.bezier_curves:
            curve_opacity_alpha_value = self.control_points_list[curve][1]

            # Plots the edge of the current iterating Bezier curve and the area it makes up in red if the user has clicked on the 'Show Areas' button,
            # the user has clicked on the 'Show Selected Curve in Contrasting Color' button,
            # and the current iterating Bezier curve matches the current Bezier curve that the user has selected.
            if curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.bezier_curves[curve].set(facecolor = (1, 0, 0, curve_opacity_alpha_value), edgecolor = (1, 0, 0, curve_opacity_alpha_value))
            
            # Plots only the edge of the current iterating Bezier curve in red if the user has only clicked on the
            # 'Show Selected Curve in Contrasting Color' button and the current iterating Bezier curve matches the current Bezier curve that the user has selected.
            elif curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == False:
                self.bezier_curves[curve].set(facecolor = 'None', edgecolor = (1, 0, 0, curve_opacity_alpha_value))

            # Plots the edge of the current iterating Bezier curve and the area it makes up in black if the user has only clicked on 
            # the 'Show Areas' button and the current iterating Bezier curve matches the current Bezier curve that the user has selected.
            elif curve == self.Curve_box.currentText() and self.contrast_curve == False and self.show_areas == True:
                self.bezier_curves[curve].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = (0, 0, 0, curve_opacity_alpha_value))
            else:

                # Plots the edge of the current iterating Bezier curve and the area it makes up in black if the user has clicked on the 'Show Areas' button. 
                if self.show_areas == True:
                    self.bezier_curves[curve].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = (0, 0, 0, curve_opacity_alpha_value))

                # Plots only the edge of the current iterating Bezier curve in black if all of other if/elif statements have failed. 
                else:
                    self.bezier_curves[curve].set(facecolor = 'None', edgecolor = (0, 0, 0, curve_opacity_alpha_value))
                self.axes.add_patch(self.bezier_curves[curve])

        # Iterates through each line area that the user has created for filling in areas of the projection screen using lines.
        for area in self.line_area_shapes:
            curve_opacity_alpha_value = self.line_area_points[area][1]

            if area == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.line_area_shapes[area].set(facecolor = (1, 0, 0, curve_opacity_alpha_value), edgecolor = 'None')
            elif area == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == False:
                self.line_area_shapes[area].set(facecolor = 'None', edgecolor = 'None')
            elif area == self.Curve_box.currentText() and self.contrast_curve == False and self.show_areas == True:
                self.line_area_shapes[area].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = 'None')
            else:
                if self.show_areas == True:
                    self.line_area_shapes[area].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = 'None')
                else:
                    self.line_area_shapes[area].set(facecolor = 'None', edgecolor = 'None')
                self.axes.add_patch(self.line_area_shapes[area])

        if self.Curve_box.currentText() in self.bezier_curves:
            self.axes.add_patch(self.bezier_curves[self.Curve_box.currentText()])
        if self.Curve_box.currentText() in self.line_area_shapes.keys():
            self.axes.add_patch(self.line_area_shapes[self.Curve_box.currentText()])

        self.axes.set_title(self.Client_projectors_box.currentText() + ' Mask')
        self.axes.set_xlabel('Screen Width')
        self.axes.set_ylabel('Screen Height')
        self.axes.set_xlim((0 - self.boundary_size * 3, self.window_width + self.boundary_size * 3))
        self.axes.set_ylim((0 - self.boundary_size * 3, self.window_height + self.boundary_size * 3))
        self.axes.grid(color = 'k')
        self.canvas.draw() 

    def setCurve(self):      
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

                user_curve_opacity_alpha_value = round(float(self.Curve_opacity_box.cleanText()) / 100, 2)
            else: 
                return
            
            user_control_point_values =  [(user_control_point_1_x, user_control_point_1_y), 
                                          (user_control_point_2_x, user_control_point_2_y), 
                                          (user_control_point_3_x, user_control_point_3_y), 
                                          (user_control_point_4_x, user_control_point_4_y)]

            curve_type = 'curve'

            if len(set(user_control_point_values)) == 2:
                curve_type = 'line'

            if self.evaluateControlPoints(user_control_point_values = user_control_point_values, curve_type = curve_type) == 'Invalid':
                return

            self.control_points_list[self.Curve_box.currentText()] = [user_control_point_values, user_curve_opacity_alpha_value]
            self.bezier_curves[self.Curve_box.currentText()] = PathPatch(Path(user_control_point_values, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), transform = self.axes.transData)

            if self.Curve_box.currentText() in self.line_area_shapes:
                del self.line_area_points[self.Curve_box.currentText()]
                del self.line_area_shapes[self.Curve_box.currentText()]

            self.redrawCanvas()
            
            if curve_type == 'line':
                self.enableFillLineButtons(line_name = self.Curve_box.currentText(), new_control_points = user_control_point_values, opacity_alpha_value = user_curve_opacity_alpha_value)
            
            self.SendInfo()
        
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

            user_curve_opacity_alpha_value = round(float(self.Curve_opacity_box.cleanText()) / 100, 2)
        else: 
            return
        
        user_control_point_values =  [(user_control_point_1_x, user_control_point_1_y), 
                                      (user_control_point_2_x, user_control_point_2_y), 
                                      (user_control_point_3_x, user_control_point_3_y),
                                      (user_control_point_4_x, user_control_point_4_y)]

        curve_type = 'curve'

        if len(set(user_control_point_values)) == 2:
            curve_type = 'line'

        new_bezier_curve = PathPatch(Path(user_control_point_values, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), transform = self.axes.transData)
        
        new_bezier_curve_name = 'Curve ' + str(len(self.control_points_list) + 1)
        self.control_points_list[new_bezier_curve_name] = [user_control_point_values, user_curve_opacity_alpha_value]
        self.bezier_curves[new_bezier_curve_name] = new_bezier_curve

        self.Curve_box.addItem(new_bezier_curve_name)
        self.axes.add_patch(new_bezier_curve)
        self.canvas.draw()

        if self.Curve_box.currentText() == 'No Curves':
            self.Curve_box.removeItem(self.Curve_box.currentIndex())
            
            self.Set_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)
        else:
            self.Curve_box.setCurrentText('Curve ' + str(len(self.control_points_list)))

        if curve_type == 'line':
            self.enableFillLineButtons(line_name = self.Curve_box.currentText(), new_control_points = user_control_point_values, opacity_alpha_value = user_curve_opacity_alpha_value)

        self.SendInfo()

    def evaluateLineEditFields(self):

        user_control_point_values = [self.control_point_1_x_line.text(), self.control_point_2_x_line.text(), 
                                     self.control_point_3_x_line.text(), self.control_point_4_x_line.text(), 
                                     self.control_point_1_y_line.text(), self.control_point_2_y_line.text(), 
                                     self.control_point_3_y_line.text(), self.control_point_4_y_line.text()]

        for control_point_value in user_control_point_values:
            if re.fullmatch("[-]?[0-9]+[.]?[0-9]*", str(control_point_value)) == None:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Invalid control point values! Values for control points cannot include letters, symbols, or spaces.')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'

        return 'Valid'

    #   All four control points cannot have the same coordinate
    #   Control Points 1 and 4 cannot be at the same point if Control Points 2 and 3 are at the same point.
    #   Either Control Points 1 or 4 have to be on the boundary lines for lines
    def evaluateControlPoints(self, user_control_point_values, curve_type):  
        if len(set(user_control_point_values)) == 1:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Invalid control points! All four control points cannot be on the same coordinate.')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'  
        
        if curve_type == 'curve':
            if user_control_point_values[0][0] == user_control_point_values[3][0] and user_control_point_values[0][1] == user_control_point_values[3][1]:
                if user_control_point_values[1][0] == user_control_point_values[2][0] and user_control_point_values[1][1] == user_control_point_values[2][1]:
                    failedMessageBox = QMessageBox()
                    failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                    failedMessageBox.setText('Invalid control points! Control point 1 and control point 4 cannot be the same if control point 2 and control point 3 are the same.')
                    failedMessageBox.setStandardButtons(QMessageBox.Ok)
                    failedMessageBox.exec()
                    return 'Invalid'
            else:         
                return 'Valid'
        else:    
            if user_control_point_values[0][0] == user_control_point_values[3][0] and user_control_point_values[0][1] == user_control_point_values[3][1]:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Control points 1 and 4 cannot be on the same coordinate for lines!')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'


            # Control Points 1 and 4 are within blue dashed lines
            if (not (user_control_point_values[0][0] < 0 or user_control_point_values[0][0] > self.window_width or user_control_point_values[0][1] < 0 or user_control_point_values[0][1] > self.window_height)
                and not (user_control_point_values[3][0] < 0 or user_control_point_values[3][0] > self.window_width or user_control_point_values[3][1] < 0 or user_control_point_values[3][1] > self.window_height)):
                if ((user_control_point_values[0][0] != 0 and user_control_point_values[0][0] != self.window_width and user_control_point_values[0][1] != 0 and user_control_point_values[0][1] != self.window_height)
                    and (user_control_point_values[3][0] != 0 and user_control_point_values[3][0] != self.window_width and user_control_point_values[3][1] != 0 and user_control_point_values[3][1] != self.window_height)):
                    failedMessageBox = QMessageBox()
                    failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                    failedMessageBox.setText('Neither Control Points 1 or 4 are on the blue dashed lines!')
                    failedMessageBox.setStandardButtons(QMessageBox.Ok)
                    failedMessageBox.exec()
                    return 'Invalid'
                else:
                    return 'Valid'
            else:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Control Points 1 or 4 are NOT within blue dashed lines!')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'
        
    def enableFillLineButtons(self, line_name, new_control_points, opacity_alpha_value):

        self.Client_projectors_box.setEnabled(False)
        self.Curve_box.setEnabled(False)
        self.Curve_opacity_box.setEnabled(False)

        self.Back_btn.setEnabled(False)

        self.control_point_1_x_line.setEnabled(False)
        self.control_point_1_y_line.setEnabled(False)
        self.control_point_2_x_line.setEnabled(False)
        self.control_point_2_y_line.setEnabled(False)
        self.control_point_3_x_line.setEnabled(False)
        self.control_point_3_y_line.setEnabled(False)
        self.control_point_4_x_line.setEnabled(False)
        self.control_point_4_y_line.setEnabled(False)

        self.Add_curve_btn.setEnabled(False)
        self.Remove_curve_btn.setEnabled(False)

        self.Control_point_1_btn.setEnabled(False)
        self.Control_point_2_btn.setEnabled(False)
        self.Control_point_3_btn.setEnabled(False)
        self.Control_point_4_btn.setEnabled(False)

        self.control_point_1_click_cursor_enable = False
        self.control_point_2_click_cursor_enable = False
        self.control_point_3_click_cursor_enable = False
        self.control_point_4_click_cursor_enable = False

        self.control_point_1_click_count_parity = 0
        self.control_point_2_click_count_parity = 0
        self.control_point_3_click_count_parity = 0
        self.control_point_4_click_count_parity = 0

        self.Line_mode_btn.setEnabled(False)
        self.line_mode_on = False
        self.line_mode_click_count_parity = 0
        
        self.Set_curve_btn.setEnabled(False)

        self.Curve_box.setEnabled(False)

        self.line_control_point_name = line_name
        self.line_control_point_1 = new_control_points[0]
        self.line_control_point_4 = new_control_points[3]

        self.line_opacity_alpha_value = opacity_alpha_value

        if self.line_control_point_1[1] == self.line_control_point_4[1]:
            self.Left_line_btn.setEnabled(False)
            self.Right_line_btn.setEnabled(False)
            self.Above_line_btn.setEnabled(True)
            self.Below_line_btn.setEnabled(True)

        elif self.line_control_point_1[0] == self.line_control_point_4[0]:
            self.Left_line_btn.setEnabled(True)
            self.Right_line_btn.setEnabled(True)
            self.Above_line_btn.setEnabled(False)
            self.Below_line_btn.setEnabled(False)
        
        else:
            self.Left_line_btn.setEnabled(True)
            self.Right_line_btn.setEnabled(True)
            self.Above_line_btn.setEnabled(True)
            self.Below_line_btn.setEnabled(True)
    
    def fillLineAreaLeft(self):
        if self.line_control_point_1[1] == 0:  
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, 0.0)]                                        
        elif self.line_control_point_4[1] == 0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, 0.0)]
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, float(self.window_height))]
        elif self.line_control_point_4[1] == float(self.window_height):
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, float(self.window_height))]
        elif self.line_control_point_1[0] == 0:
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        elif self.line_control_point_4[0] == 0:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(0.0, self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_1[1])]
        else:
            control_points_line_area = [(0.0, self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_4[1])]
        
        self.makeFillArea(control_points_line_area)
        self.SendInfo()
            
    def fillLineAreaRight(self):
        if self.line_control_point_1[1] == 0:
            control_points_line_area = [(float(self.window_width), 0.0),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (float(self.window_width), 0.0)]   
        elif self.line_control_point_4[1] == 0: 
            control_points_line_area = [(float(self.window_width), 0.0),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), 0.0)]      
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]), 
                                        (float(self.window_width), float(self.window_height))]
        elif self.line_control_point_4[1] == float(self.window_height):
            control_points_line_area = [(float(self.window_width), float(self.window_height)),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), float(self.window_height))]     
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]  
        elif self.line_control_point_4[0] == float(self.window_width):
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]
        elif self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(float(self.window_width), self.line_control_point_1[1]),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (float(self.window_width), self.line_control_point_1[1])]  
        else:
            control_points_line_area = [(float(self.window_width), self.line_control_point_4[1]),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), self.line_control_point_4[1])] 
            
        self.makeFillArea(control_points_line_area)
        self.SendInfo()

    def fillLineAreaAbove(self):
        if self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (0.0, float(self.window_height))]
            
        elif self.line_control_point_4[0] == 0.0:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (0.0, float(self.window_height))]
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (float(self.window_width), float(self.window_height))]
        elif self.line_control_point_4[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (float(self.window_width), float(self.window_height))]
        elif self.line_control_point_1[1] == 0.0:
            control_points_line_area = [(self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_1[0], float(self.window_height))]
        elif self.line_control_point_4[1] == 0.0:
            control_points_line_area = [(self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_4[0], float(self.window_height))]
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        else:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]

        self.makeFillArea(control_points_line_area)
        self.SendInfo()

    def fillLineAreaBelow(self):
        if self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], 0.0),
                                        (0.0, 0.0)]
        elif self.line_control_point_4[0] == 0.0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], 0.0),
                                        (0.0, 0.0)]
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], 0.0),
                                        (float(self.window_width), 0.0)]
        elif self.line_control_point_4[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], 0.0),
                                        (float(self.window_width), 0.0)]
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(self.line_control_point_1[0], 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], 0.0),
                                        (self.line_control_point_1[0], 0.0)]
        elif self.line_control_point_4[1] == float(self.window_height):
            control_points_line_area = [(self.line_control_point_4[0], 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], 0.0),
                                        (self.line_control_point_4[0], 0.0)]
        elif self.line_control_point_1[1] == 0.0:
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], 0.0),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        else:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], 0.0),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]      
        
        self.makeFillArea(control_points_line_area)
        self.SendInfo()
            
    def makeFillArea(self, control_points_line_area):

            self.Left_line_btn.setEnabled(False)
            self.Right_line_btn.setEnabled(False)
            self.Above_line_btn.setEnabled(False)
            self.Below_line_btn.setEnabled(False)

            self.line_area_points[self.line_control_point_name] = [control_points_line_area, self.line_opacity_alpha_value]
            self.line_area_shapes[self.line_control_point_name] = PathPatch(Path(control_points_line_area, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), transform=self.axes.transData)

            self.redrawCanvas()

            self.Client_projectors_box.setEnabled(True)
            self.Curve_box.setEnabled(True)
            self.Curve_opacity_box.setEnabled(True)

            self.Back_btn.setEnabled(True)

            self.control_point_1_x_line.setEnabled(True)
            self.control_point_1_y_line.setEnabled(True)
            self.control_point_2_x_line.setEnabled(True)
            self.control_point_2_y_line.setEnabled(True)
            self.control_point_3_x_line.setEnabled(True)
            self.control_point_3_y_line.setEnabled(True)
            self.control_point_4_x_line.setEnabled(True)
            self.control_point_4_y_line.setEnabled(True)

            self.Line_mode_btn.setEnabled(True)

            self.Add_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)

            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)

            self.Set_curve_btn.setEnabled(True)

            self.Curve_box.setEnabled(True)

    def removeCurveClicked(self):

        if self.Curve_box.currentText() == 'No Curves':
            return
        else:
            
            removed_curve_number = int(str.split(self.Curve_box.currentText(), ' ')[1])
            removed_curve_key_name = 'Curve ' + str(removed_curve_number)

            total_curves_before_removal = len(self.bezier_curves)

            if removed_curve_number < total_curves_before_removal:
                changed_curves = []
                index = removed_curve_number + 1

                while index <= total_curves_before_removal:
                    changed_curves.append('Curve ' + str(index))
                    index = index + 1

                if removed_curve_key_name in self.line_area_points and len(self.line_area_points) == 1 and len(self.control_points_list) == 1:
                    del self.control_points_list[removed_curve_key_name]
                    del self.bezier_curves[removed_curve_key_name]
                    del self.line_area_points[removed_curve_key_name]
                    del self.line_area_shapes[removed_curve_key_name]

                else:
                    for changed_curve in changed_curves:
                        new_curve_number = int(str.split(changed_curve, ' ')[1]) - 1

                        if new_curve_number == removed_curve_number:
                            if removed_curve_key_name in self.line_area_points:
                                del self.control_points_list[removed_curve_key_name]
                                del self.bezier_curves[removed_curve_key_name]
                                del self.line_area_points[removed_curve_key_name]
                                del self.line_area_shapes[removed_curve_key_name]
                        
                        self.control_points_list['Curve ' + str(new_curve_number)] = self.control_points_list[changed_curve]
                        del self.control_points_list[changed_curve]

                        self.bezier_curves['Curve ' + str(new_curve_number)] = self.bezier_curves[changed_curve]
                        del self.bezier_curves[changed_curve]
                        
                        if changed_curve in self.line_area_points:
                            self.line_area_points['Curve ' + str(new_curve_number)] = self.line_area_points[changed_curve]
                            del self.line_area_points[changed_curve]

                            self.line_area_shapes['Curve ' + str(new_curve_number)] = self.line_area_shapes[changed_curve]
                            del self.line_area_shapes[changed_curve]
                
                self.Curve_box.clear()
                self.Curve_box.addItems(list(self.bezier_curves.keys()))

            else:
                del self.control_points_list[self.Curve_box.currentText()]
                del self.bezier_curves[self.Curve_box.currentText()]

                if self.Curve_box.currentText() in self.line_area_points:
                    del self.line_area_points[self.Curve_box.currentText()]
                    del self.line_area_shapes[self.Curve_box.currentText()]

                if not self.bezier_curves.keys():
                    self.Curve_box.addItem('No Curves')

                    self.Set_curve_btn.setEnabled(False)
                    self.Remove_curve_btn.setEnabled(False)

                self.Curve_box.removeItem(self.Curve_box.currentIndex())
            
            self.redrawCanvas()
            self.SendInfo()

    def selectedCurveChanged(self):
        
        if self.Curve_box.currentText() == 'No Curves' or self.Curve_box.currentText() == '':
            return
        else:
            selected_curve_control_points = self.control_points_list[self.Curve_box.currentText()][0]
            selected_curve_opacity_alpha_value = self.control_points_list[self.Curve_box.currentText()][1]

            self.control_point_1_x_line.setText(str(selected_curve_control_points[0][0]))
            self.control_point_1_y_line.setText(str(selected_curve_control_points[0][1]))
            self.control_point_2_x_line.setText(str(selected_curve_control_points[1][0]))
            self.control_point_2_y_line.setText(str(selected_curve_control_points[1][1]))
            self.control_point_3_x_line.setText(str(selected_curve_control_points[2][0]))
            self.control_point_3_y_line.setText(str(selected_curve_control_points[2][1]))
            self.control_point_4_x_line.setText(str(selected_curve_control_points[3][0]))
            self.control_point_4_y_line.setText(str(selected_curve_control_points[3][1]))

            self.Curve_opacity_box.setValue(selected_curve_opacity_alpha_value * 100)

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
            self.contrast_curve_click_count_parity = 0
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
    
    def setMouseCursorCoordinates(self, cursor_x, cursor_y, x_line_edit, y_line_edit):
        if cursor_x != None and cursor_y != None:
            if abs(cursor_x - 0) <= 10.0 and cursor_y >= 0 and cursor_y <= self.window_height:
                x_line_edit.setText('0.0')
                y_line_edit.setText(str(round(cursor_y, 2)))
            elif abs(cursor_x - self.window_width) <= 10.0 and cursor_y >= 0 and cursor_y <= self.window_height:
                x_line_edit.setText(str(self.window_width))
                y_line_edit.setText(str(round(cursor_y, 2)))
            elif abs(cursor_y - 0) <= 10.0 and cursor_x >= 0 and cursor_x <= self.window_width:
                x_line_edit.setText(str(round(cursor_x, 2)))
                y_line_edit.setText('0.0')
            elif abs(cursor_y - self.window_height) <= 10.0 and cursor_x >= 0 and cursor_x <= self.window_width:
                x_line_edit.setText(str(round(cursor_x, 2)))
                y_line_edit.setText(str(self.window_height))
            elif abs(cursor_x - 0.0) <= 10.0 and abs(cursor_y - self.window_height) <= 10.0:
                x_line_edit.setText('0.0')
                y_line_edit.setText(str(self.window_height))
            elif abs(cursor_x - 0.0) <= 10.0 and abs(cursor_y - 0.0) <= 10.0:
                x_line_edit.setText('0.0')
                y_line_edit.setText('0.0')
            elif abs(cursor_x - self.window_width) <= 10.0 and abs(cursor_y - 0.0) <= 10.0:
                x_line_edit.setText(str(self.window_width))
                y_line_edit.setText('0.0')
            elif abs(cursor_x - self.window_width) <= 10.0 and abs(cursor_y - self.window_height) <= 10.0:
                x_line_edit.setText(str(self.window_width))
                y_line_edit.setText(str(self.window_height))
            else:
                x_line_edit.setText(str(round(cursor_x, 2)))
                y_line_edit.setText(str(round(cursor_y, 2)))

    def leftMouseClicked(self, event):
        if event.button == MouseButton.LEFT:
            if self.control_point_1_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_1_x_line, self.control_point_1_y_line)
                self.setCurve()

            elif self.control_point_2_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_2_x_line, self.control_point_2_y_line)
                self.setCurve()

            elif self.control_point_3_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_3_x_line, self.control_point_3_y_line)
                self.setCurve()
            
            elif self.control_point_4_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_4_x_line, self.control_point_4_y_line)
                self.setCurve()

    def lineModeClicked(self):

        if self.control_point_1_click_cursor_enable == True or self.control_point_4_click_cursor_enable == True:
            return
        
        self.line_mode_click_count_parity = self.line_mode_click_count_parity + 1

        if self.line_mode_click_count_parity % 2 == 0:
            self.Control_point_2_btn.setEnabled(True)
            self.control_point_2_x_line.setEnabled(True)
            self.control_point_2_y_line.setEnabled(True)

            self.Control_point_3_btn.setEnabled(True)
            self.control_point_3_x_line.setEnabled(True)
            self.control_point_3_y_line.setEnabled(True)

            self.line_mode_on = False
            self.line_mode_click_count_parity = 0
        
        else:
            self.Control_point_2_btn.setEnabled(False)
            self.control_point_2_x_line.setEnabled(False)
            self.control_point_2_y_line.setEnabled(False)

            self.control_point_2_x_line.setText(self.control_point_1_x_line.text())
            self.control_point_2_y_line.setText(self.control_point_1_y_line.text())

            self.Control_point_3_btn.setEnabled(False)
            self.control_point_3_x_line.setEnabled(False)
            self.control_point_3_y_line.setEnabled(False)

            self.control_point_3_x_line.setText(self.control_point_1_x_line.text())
            self.control_point_3_y_line.setText(self.control_point_1_y_line.text())

            self.line_mode_on = True

    def controlPoint1XChanged(self):
        if self.line_mode_on == True:
            self.control_point_2_x_line.setText(self.control_point_1_x_line.text())
            self.control_point_3_x_line.setText(self.control_point_1_x_line.text())
    
    def controlPoint1YChanged(self):
        if self.line_mode_on == True:
            self.control_point_2_y_line.setText(self.control_point_1_y_line.text())
            self.control_point_3_y_line.setText(self.control_point_1_y_line.text())

    ## Client combo box text changed signal
    #
    # Checks whether the client combo box was changed and updates the bezier info from that particular client
    def clientComboBoxChanged(self):
        self.axes.clear()
        self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')
        self.bezier_curves.clear()
        self.line_area_shapes.clear()
        self.line_mode_on = False
        self.line_mode_click_count_parity = 0
        try:
            self.GetInfo()
            self.Line_mode_btn.setEnabled(True)
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)
            self.Set_curve_btn.setEnabled(True)
            self.Add_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)
            self.Show_contrast_curve_btn.setEnabled(True)
            self.Show_areas_btn.setEnabled(True)
            self.Show_control_points_btn.setEnabled(True)
            if(self.control_points_list or self.line_area_points):
                for pointName, pointValue in self.control_points_list.items():
                    self.bezier_curves[pointName] = PathPatch(Path(pointValue[0], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
            
                for curve in self.bezier_curves:
                    self.axes.add_patch(self.bezier_curves[curve])

                for lineName, lineValue in self.line_area_points.items():
                    self.line_area_shapes[lineName] = PathPatch(Path(lineValue[0], [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), facecolor = 'none', transform=self.axes.transData)

                for line in self.line_area_shapes:
                    self.axes.add_patch(self.line_area_shapes[line])

                selected_curve_opacity_alpha_value = self.control_points_list["Curve 1"][1]
                self.Curve_opacity_box.setValue(selected_curve_opacity_alpha_value * 100)

                '''
            else:
                control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
                control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
                control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
                print ("test")
                initial_sets_of_control_points = [control_points_1, control_points_2, control_points_3]

                self.index = 0

                for control_points in initial_sets_of_control_points:
                    self.index = self.index + 1
                    self.control_points_list['Curve ' + str(self.index)] = [control_points, 1.0]
                    self.bezier_curves['Curve ' + str(self.index)] = PathPatch(Path(control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
                
                for curve in self.bezier_curves:
                    self.axes.add_patch(self.bezier_curves[curve])

                self.SendInfo()
                '''
        except:
            self.Line_mode_btn.setEnabled(False)
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.Set_curve_btn.setEnabled(False)
            self.Add_curve_btn.setEnabled(False)
            self.Remove_curve_btn.setEnabled(False)
            self.Show_contrast_curve_btn.setEnabled(False)
            self.Show_areas_btn.setEnabled(False)
            self.Show_control_points_btn.setEnabled(False)
            
            errorBox = QMessageBox()
            errorBox.setWindowTitle('Connection Error - Planetarium Edge Blend')
            errorBox.setText("Client at IP Address not found. Are you sure the client application is running on it?")
            errorBox.exec()

            self.axes.set_title('Not connected to ' + self.Client_projectors_box.currentText())
        
        self.Curve_box.clear()
        self.Curve_box.addItems(list(self.bezier_curves.keys()))
        self.setTextBoxes()    
        self.axes.set_xlim((0 - self.boundary_size * 3, self.window_width + self.boundary_size * 3))
        self.axes.set_ylim((0 - self.boundary_size * 3, self.window_height + self.boundary_size * 3))
        self.axes.grid(color = 'k')
        self.canvas.draw() 

    ###########################################################
    # NETWORKING
    ###########################################################

    ## Retrieves bezier curve information from a given client
    #
    # Uses the Clients combo box (Client_projectors_box) and the client_IP.txt file to get the current client
    def GetInfo(self):
        ## IP of the currently selected client
        clientIP = self.client_servers_IP_addresses[self.Client_projectors_box.currentText()]

        ## QTcpSocket variable representing the host side connection with the client.
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(clientIP, self.PORT, QIODevice.ReadWrite)
        self.tcpSocket.waitForConnected(2000)

        ## Variable containing information to indicate that the client should send information back
        toSend = "send"
        toSend = pickle.dumps(toSend, -1)

        # Send the info to the client
        self.tcpSocket.write(toSend)
        
        # Wait for the client's response
        self.tcpSocket.waitForReadyRead()

        ## Read in the information from the client. Will be in the format of an array of two dictionaries
        arrayIn = pickle.loads(self.tcpSocket.readAll())
        self.control_points_list = arrayIn[0]
        self.line_area_points = arrayIn[1]
        self.window_width = arrayIn[2]
        self.window_height = arrayIn[3]
        self.boundaries_x = [0, 0, self.window_width, self.window_width, 0]
        self.boundaries_y = [self.window_height, 0, 0, self.window_height, self.window_height]

    ## Sends bezier curve information to a given client
    #
    # Uses the Clients combo box (Client_projectors_box) and the client_IP.txt file to get the current client
    def SendInfo(self):
        ## IP of the currently selected client
        clientIP = self.client_servers_IP_addresses[self.Client_projectors_box.currentText()]

        ## QTcpSocket variable representing the host side connection with the client.
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(clientIP, self.PORT, QIODevice.ReadWrite)
        self.tcpSocket.waitForConnected(5000)

        ## Variable containing bezier information to send to client
        toSend = [self.control_points_list, self.line_area_points]
        toSend = pickle.dumps(toSend, -1)

        # Sends to client
        self.tcpSocket.write(toSend)
        self.tcpSocket.waitForReadyRead()

        # (Not necessary, loads a confirmation from client, may be useful)
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

    ## Fetches the list of clients from client_ip.txt and puts it into the Client_list list widget
    #
    #
    def listClients(self):
        # Clear the list
        self.Client_list.clear()

        # Read all the clients
        with open("client_ip.txt", "r") as clients:
            ips = clients.readlines()
        for ip in ips:
            if ip.strip() != "":
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

    ## If an item in the list is clicked, allow user to edit and take the information from there into the edit textedits
    #
    #
    def listItemClicked(self):
        self.Edit_name.setEnabled(True)
        self.Edit_IP.setEnabled(True)
        self.Edit_btn.setEnabled(True)
        self.Delete_btn.setEnabled(True)
        self.Edit_name.setText(self.Client_list.currentItem().text().split('-')[0])
        self.Edit_IP.setText(self.Client_list.currentItem().text().split('-')[1])
        
    ## This function adds a client to the client_ip.txt file
    #
    #
    def addClient(self):
        # If either the name or IP are blank you are disallowed from adding it.
        if self.Add_name.text() != "" and self.Add_IP.text() != "":
            # This regular expression matches with an IPv4 address, any IP added SHOULD be let through.
            if not re.fullmatch("((([0-9])|([1-9][0-9])|([1][0-9][0-9])|([2][0-4][0-9])|([2][5][0-5]))[.]){3}(([0-9])|([1-9][0-9])|([1][0-9][0-9])|([2][0-4][0-9])|([2][5][0-5]))", self.Add_IP.text()):
                # If the IP address is invalid, open an error message informing the user.
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Projection Configuration Error - Planetarium Edge Blend')
                failedMessageBox.setText("Enter a valid IP address.")
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return

            # If valid, append the client to the end of client_ip.txt
            with open("client_ip.txt", "a") as clients:
                if self.Client_list.count() == 0:
                    clients.write(self.Add_name.text() + "-" + self.Add_IP.text())
                else:
                    clients.write("\n" + self.Add_name.text() + "-" + self.Add_IP.text())

            # List clients again to refresh
            self.listClients()

    ## This function edits an existing line in the client_ip.txt file
    #
    #
    def editClient(self):
        # If either the name or IP are blank you are disallowed from committing that edit.
        if self.Edit_name.text() != "" and self.Edit_IP.text() != "":
            # This regular expression matches with an IPv4 address, any IP added SHOULD be let through.
            if not re.fullmatch("((([0-9])|([1-9][0-9])|([1][0-9][0-9])|([2][0-4][0-9])|([2][5][0-5]))[.]){3}(([0-9])|([1-9][0-9])|([1][0-9][0-9])|([2][0-4][0-9])|([2][5][0-5]))", self.Edit_IP.text()):
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Projection Configuration Error - Planetarium Edge Blend')
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
                        ips[i] = self.Edit_name.text() + "-" + self.Edit_IP.text()
                    else:
                        ips[i] = self.Edit_name.text() + "-" + self.Edit_IP.text() + "\n"
                    break

            # Re-open the client_ip.txt file for editing and re-write the list
            clients = open("client_ip.txt", "w")
            for ip in ips:
                if ip.strip() != "":
                    clients.write(ip)
            clients.close()

            # List clients again to refresh
            self.listClients()
    
    ## Allows the user to delete clients from the list
    def deleteClient(self):
        ## Message box to confirm the user wishes to delete the client
        confirmMessageBox = QMessageBox()
        confirmMessageBox.setWindowTitle('Projector Configuration - Planetarium Edge Blend')
        confirmMessageBox.setText("Are you sure you want to delete this client?")
        confirmMessageBox.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        confirmMessageBox.setDefaultButton(QMessageBox.Cancel)

        ## Result of message box dialog (either OK or Cancel)
        result = confirmMessageBox.exec()

        # Only delete if result is ok, if cancel, do nothing
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
                if ip.strip() != "":
                    clients.write(ip)
            clients.close()
            self.listClients()

            

# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    mainWindow = MainWindow()
    widget.addWidget(mainWindow)
    #widget.setFixedHeight(900)
    #widget.setFixedWidth(1531)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
