import sys 
import re
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QIODevice

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backend_bases import MouseButton

import matplotlib
import matplotlib.pyplot as plt        
matplotlib.use('Qt5Agg')

import pickle

# This file contains all the functionalities of the widgets between the windows.
class MainWindow(QMainWindow):
    
    # Loads the main window by default when the user boots up the host GUI.
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("MainWindow.ui", self)
        widget.setWindowTitle('Planetarium Edge Blend')
        self.MaskFeedGeometryEdit_btn.clicked.connect(self.gotoMaskFeedAndGeometryEditingWindow)
        self.ProjectorConfig_btn.clicked.connect(self.gotoProjectorConfigurationWindow)

    # Switches to the 'Mask Feed and Geometry Editing - Planetarium Edge Blend' window if the user presses on the 
    # 'Mask Feed and Geometry Editing' button on the main window.
    def gotoMaskFeedAndGeometryEditingWindow(self):
        geometryEdit = MaskFeedAndGeometryEditingWindow()
        widget.setWindowTitle('Mask Feed and Geometry Editing - Planetarium Edge Blend')
        widget.addWidget(geometryEdit)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # Switches to the 'Projector Configuration - Planetarium Edge Blend' window if the user presses on the
    #'Projector Configuration - Planetarium Edge Blend' button on the main window.
    def gotoProjectorConfigurationWindow(self):
        projectorConfig = ProjectorConfigurationWindow()
        widget.setWindowTitle('Projector Configuration - Planetarium Edge Blend')
        widget.addWidget(projectorConfig)
        widget.setCurrentIndex(widget.currentIndex() + 1)

'''
MASK FEED AND GEOMETRY EDITING
'''

## Represents the 'Mask Feed and Geometry Editing - Planetarium Edge Blend' window for the host GUI.
class MaskFeedAndGeometryEditingWindow(QMainWindow):
    def __init__(self):
        super(MaskFeedAndGeometryEditingWindow, self).__init__()
        loadUi("MaskFeedAndGeometryEditingWindow.ui", self)

        ## The width of the client projector screen that the user has selected to view
        self.window_width = 1920

        ## The height of the client projector screen that the user has selected to view
        self.window_height = 1200

        ## Size of the area outside of the blue dashed lines on the mask graph.
        self.boundary_size = 300

        ## X coordinates of plotting the blue dashed lines on the mask graph.
        self.boundaries_x = [0, 0, self.window_width, self.window_width, 0]

        ## Y coordinates of plotting the blue dashed lines on the mask graph.
        self.boundaries_y = [self.window_height, 0, 0, self.window_height, self.window_height]

        ## Determines whether to register the user's mouse cursor coordinates for control point 1.
        self.control_point_1_click_cursor_enable = False

        ## Determines whether to register the user's mouse cursor coordinates for control point 2.
        self.control_point_2_click_cursor_enable = False

        ## Determines whether to register the user's mouse cursor coordinates for control point 3.
        self.control_point_3_click_cursor_enable = False

        ## Determines whether to register the user's mouse cursor coordinates for control point 4.
        self.control_point_4_click_cursor_enable = False

        ## Counter for how many times the user has pressed on the 'Control Point 1' button.
        self.control_point_1_click_count_parity = 0

        ## Counter for how many times the user has pressed on the 'Control Point 2' button.
        self.control_point_2_click_count_parity = 0

        ## Counter for how many times the user has pressed on the 'Control Point 3' button.
        self.control_point_3_click_count_parity = 0

        ## Counter for how many times the user has pressed on the 'Control Point 4' button.
        self.control_point_4_click_count_parity = 0

        ## Counter for how many times the user has pressed on the 'Line Mode' button.
        self.line_mode_click_count_parity = 0

        ## Dictates whether line mode is on.
        self.line_mode_on = False

        ## Counter for how many times the user has pressed on the 'Show Selected Curve in Contrasting Color' button.
        self.contrast_curve_click_count_parity = 0

        ## Dictates whether to show the Bezier curve that the user has selected in a red color.
        self.contrast_curve = False

        ## Counter for how many times the user has pressed on the 'Show Areas' button.
        self.show_areas_click_count_parity = 0

        ## Dictates whether to show the areas of all user-created Bezier curves.
        self.show_areas = False

        ## Counter for how many times the user has pressed on the 'Show Control Points' button.
        self.show_control_points_click_count_parity = 0

        ## Dictates whether to show the control points of the Bezier curve that the user has selected.
        self.show_control_points = False

        # Creates the mask graph.
        figure, self.axes = plt.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        # Connects the left mouse button signal to the mask graph and puts the mask graph onto the window.
        plt.connect('button_press_event', self.leftMouseClicked)
        self.Mask_graph_layout.addWidget(self.canvas)
        
        ## Dictionary containing the control points used for Bezier curves.
        # The exact format of the control_points_list is {"Curve number" : [[control points], opacity]}.
        # Curve number is the associated number of the curve. 
        # [control points] is an array containing all the control points for the curve. 
        # opacity is a value from 0 to 1 containing the opacity value used for drawing the area of the curve.
        self.control_points_list = {}

        ## Dictionary containing generated Bezier curves based on the control points.
        self.bezier_curves = {}

        ## Dictionary containing "line" type Bezier curves.
        # Lines are defined as Bezier curves with only two unique control points. The other two control points have equal coordinates to either of the unique control points.
        # The reason lines are defined separately from normal Bezier curves is due to the way we draw areas pertaining to lines, which has to be done more manually.
        self.line_area_points = {}

        ## Dictionary containing the shapes for areas under lines.
        self.line_area_shapes = {}

        ## Dictionary containing names and IP addresses of clients
        self.client_servers_IP_addresses = {}

        ## Port number used for incoming TCP Connections over the local network.
        self.PORT = 64012

        self.retrieveProjectors()

        # Attempt to get info from the first client in the client list.
        try:
            self.GetInfo()
            # If the info contains at least one Bezier curve or line we redraw them on the host for editing.
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

            # Sets the axis information for the figure used for Bezier curves.
            self.axes.set_title(self.Client_projectors_box.currentText() + ' Mask')
            self.axes.set_xlabel('Screen Width')
            self.axes.set_ylabel('Screen Height')
            self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')
            self.axes.set_xlim((0 - self.boundary_size, self.window_width + self.boundary_size))
            self.axes.set_ylim((0 - self.boundary_size, self.window_height + self.boundary_size))

        # If GetInfo() fails to find the client, we want to set all the buttons to disabled so that the user is unable to change any curves for an unconnected client.
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

            # Display an error message when the client is not found.
            errorBox = QMessageBox()
            errorBox.setWindowTitle('Connection Error - Planetarium Edge Blend')
            errorBox.setText("Client at IP Address not found. Are you sure the client application is running on it?")
            errorBox.exec()

            self.axes.set_title('Not connected to ' + self.Client_projectors_box.currentText())

        self.axes.grid(color = 'k')
        self.canvas.draw()   

        self.setTextBoxes()
        
        # PyQt5 button connections to functions.
        self.Curve_box.currentTextChanged.connect(self.selectedCurveChanged)
        self.Client_projectors_box.currentTextChanged.connect(self.clientComboBoxChanged)

        self.Add_curve_btn.clicked.connect(self.addNewCurve)
        self.Remove_curve_btn.clicked.connect(self.removeCurve)
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

        self.Show_contrast_curve_btn.clicked.connect(self.showContrastCurve)
        self.Show_areas_btn.clicked.connect(self.showAreas)
        self.Show_control_points_btn.clicked.connect(self.showControlPoints)
        
        self.Back_btn.clicked.connect(self.gotoMainWindow)

    ## Sets the text boxes to the curve information for curve editing.
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
    # Reads the client_ip.txt file on the host computer containing all of the configured projectors' information and stores that information into a dictionary.
    def retrieveProjectors(self):
        client_servers_info_file = open('client_ip.txt', 'r')

        # Reads each line from the text line and removes the newline character before creating a key value pair in the client_servers_IP_addresses dictionary.
        for line in client_servers_info_file:
            client_server_info = str.split(line.removesuffix('\n'), '-')
            self.client_servers_IP_addresses[client_server_info[0]] = client_server_info[1]

        client_servers_info_file.close()

        # Updates the combo box so that the user can now select each of the configured projectors to view and edit a client projector mask.
        self.Client_projectors_box.addItems(self.client_servers_IP_addresses.keys())
        
    ## Clears the mask graph containing all of Bezier curves for a client projector mask and plots each Bezier curve and its corresponding line area shape again.
    def redrawCanvas(self):
        self.axes.clear()

        # Plots the blue dashed lines onto the graph.
        self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')

        # Plots the control points for the Bezier curve that the user has select in the Curve_box comboBox in a red color on the mask graph if the user has clicked on the
        # 'Show Control Points' button.
        if self.Curve_box.currentText() != 'No Curves' and self.show_control_points == True:
            for control_points in self.control_points_list[self.Curve_box.currentText()][0]:
                self.axes.plot(control_points[0], control_points[1], 'ro')

        # Iterates through each Bezier curve that the user has created and will evaluate each Bezier curve for a set of conditions before plotting them onto the graph.
        for curve in self.bezier_curves:
            curve_opacity_alpha_value = self.control_points_list[curve][1]

            # Sets the edge of the current iterating Bezier curve and the area it makes up to a red color if the 
            # current iterating Bezier curve matches the Bezier curve that the user has selected, 
            # the user has clicked on the 'Show Areas' button to be on,
            # and the user has clicked on the 'Show Selected Curve in Contrasting Color' button to be on,
            if curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.bezier_curves[curve].set(facecolor = (1, 0, 0, curve_opacity_alpha_value), edgecolor = (1, 0, 0, curve_opacity_alpha_value))
            
            # Sets only the edge of the current iterating Bezier curve to a red color if the current iterating Bezier curve matches the Bezier curve
            # that the user has select in the Curve_box comboBox and the user has only clicked on the 'Show Selected Curve in Contrasting Color' button to be on.
            elif curve == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == False:
                self.bezier_curves[curve].set(facecolor = 'None', edgecolor = (1, 0, 0, curve_opacity_alpha_value))

            # Handles the cases where the current iterating Bezier curve does not match the Bezier curve that the user has select in the Curve_box comboBox 
            # and when the user hasn't clicked on the 'Show Selected Curve in Contrasting Color' button to be on.
            else:

                # Sets the edge of the current iterating Bezier curve and the area it makes up to a black color if the user has clicked
                # on the 'Show Areas' button to be on. 
                if self.show_areas == True:
                    self.bezier_curves[curve].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = (0, 0, 0, curve_opacity_alpha_value))

                # Sets only the edge of the current iterating Bezier curve in a black color if the user hasn't clicked on the 'Show Areas' button to be on. 
                else:
                    self.bezier_curves[curve].set(facecolor = 'None', edgecolor = (0, 0, 0, curve_opacity_alpha_value))
                
                # Plots the current iterating Bezier curve onto the graph.
                self.axes.add_patch(self.bezier_curves[curve])

        # Iterates through each line area shape that the user has created for filling in areas of the projection screen using lines.
        for area in self.line_area_shapes:
            curve_opacity_alpha_value = self.line_area_points[area][1]

            # Sets the area of the current iterating line area shape to a red color if the the current iterating line area shape matches the curve 
            # that the user has selected, the user has clicked on the 'Show Selected Curve in Contrasting Color' button to be on,
            # and the user has clicked on the 'Show Areas' button to be on.
            if area == self.Curve_box.currentText() and self.contrast_curve == True and self.show_areas == True:
                self.line_area_shapes[area].set(facecolor = (1, 0, 0, curve_opacity_alpha_value), edgecolor = 'None')

            # Handles the cases where the current iterating line area shape does not match the curve that the user has select in the Curve_box comboBox and when the user hasn't clicked on
            # the 'Show Selected Curve in Contrasting Color' to be on.
            else:

                # Sets the area of the current iterating line area shape to a black color if the user has clicked on the 'Show Areas' button to be on.
                if self.show_areas == True:
                    self.line_area_shapes[area].set(facecolor = (0, 0, 0, curve_opacity_alpha_value), edgecolor = 'None')
                
                # Makes the area of the current iterating line shape nonvisible to the user if the user hasn't clicked on the 'Show Areas' button to be on.
                else:
                    self.line_area_shapes[area].set(facecolor = 'None', edgecolor = 'None')

                # Plots the current iterating line area shape onto the graph.
                self.axes.add_patch(self.line_area_shapes[area])

        # Plots the current Bezier curve that the user has select in the Curve_box comboBox onto the graph if the user has clicked on the 'Show Selected Curve in Contrasting Color' 
        # button to be on.
        if self.Curve_box.currentText() in self.bezier_curves.keys() and self.contrast_curve == True:
            self.axes.add_patch(self.bezier_curves[self.Curve_box.currentText()])
        
        # Plots the line area shape that matches the current Bezier curve that the user has select in the Curve_box comboBox onto the graph if the user has clicked on 
        # the 'Show Selected Curve in Contrasting Color' button to be on.
        if self.Curve_box.currentText() in self.line_area_shapes.keys() and self.contrast_curve == True:
            self.axes.add_patch(self.line_area_shapes[self.Curve_box.currentText()])

        # Sets the graph's visuals and draws the graph onto the GUI.
        self.axes.set_title(self.Client_projectors_box.currentText() + ' Mask')
        self.axes.set_xlabel('Screen Width')
        self.axes.set_ylabel('Screen Height')
        self.axes.set_xlim((0 - self.boundary_size, self.window_width + self.boundary_size))
        self.axes.set_ylim((0 - self.boundary_size, self.window_height + self.boundary_size))
        self.axes.grid(color = 'k')
        self.canvas.draw() 

    ## Edits the Bezier curve that the user has select in the Curve_box comboBox based on the user's inputs for the line edit fields and opacity spin box and plots it on the mask graph.
    #  This happens once the user clicks on the 'Set curve' button.
    def setCurve(self):      

        # Checks whether the values in the line edit fields are valid.
        # If the values are valid, then the convertUserInputsForCurve() function is called to convert the user values.
        if self.evaluateLineEditFields() == 'Valid':
            user_control_point_values, user_curve_opacity_alpha_value = self.convertUserInputsForCurve()

        # Stops the function call if the values in the line edit fields are invalid. 
        else: 
            return
                                        
        curve_type = 'curve'

        # Considers the Bezier curve to be a line if there are only two unique sets of xy coordinates from the user's inputs for the line edit fields.
        if len(set(user_control_point_values)) == 2:
            curve_type = 'line'

        # Stops the function call if the user's control points do not meet the conditions for valid control point rules depending on the curve type.
        if self.evaluateControlPoints(user_control_point_values = user_control_point_values, curve_type = curve_type) == 'Invalid':
            return

        # Edits the control_points_list and bezier_curves dictionaries based on the user's control points and opacity for the Bezier curve that they have selected.
        self.control_points_list[self.Curve_box.currentText()] = [user_control_point_values, user_curve_opacity_alpha_value]
        self.bezier_curves[self.Curve_box.currentText()] = PathPatch(Path(user_control_point_values, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), transform = self.axes.transData)

        # If the Bezier curve that the user has select in the Curve_box comboBox was previously considered a line before the user clicked on the 'Set Curve' button,
        # then this deletes the previous line information associated to the Bezier curve before the user changed the Bezier curve into a curve.
        if self.Curve_box.currentText() in self.line_area_shapes:
            del self.line_area_points[self.Curve_box.currentText()]
            del self.line_area_shapes[self.Curve_box.currentText()]

        self.redrawCanvas()
        
        # Disables all buttons, line edit fields, combo boxes, and the spin box until the user chooses which areas of the projection screen to fill if the user edits
        # a Bezier curve that is considered a line.
        if curve_type == 'line':
            self.enableFillLineButtons(line_name = self.Curve_box.currentText(), new_control_points = user_control_point_values, opacity_alpha_value = user_curve_opacity_alpha_value)
        
        self.SendInfo()
        
    ## Creates a new Bezier curve based on the user's inputs for the line edit fields and opacity spin box and plots it on the mask graph.
    # This happens once the user clicks on the 'Add new curve' button.
    def addNewCurve(self):

        # Checks whether the values in the line edit fields are valid.
        # If the values are valid, then the convertUserInputsForCurve() function is called to convert the user's values.
        if self.evaluateLineEditFields() == 'Valid':
            user_control_point_values, user_curve_opacity_alpha_value = self.convertUserInputsForCurve()

        # Stops the function call if the the values in the line edit fields are not valid.
        else: 
            return
                                      
        curve_type = 'curve'

        # Considers the Bezier curve a line if there are only two unique sets of coordinates from the user's inputs for the line edit fields.
        if len(set(user_control_point_values)) == 2:
            curve_type = 'line'

        # Stops the function call if the user's control points do not meet the conditions for valid control point rules depending on the curve type.
        if self.evaluateControlPoints(user_control_point_values = user_control_point_values, curve_type = curve_type) == 'Invalid':
            return

        # Adds a new key value pair into the control_points_list and bezier_curves dictionaries based on the user's inputs for the line edit fields and spin box. 
        new_bezier_curve_name = 'Curve ' + str(len(self.control_points_list) + 1)
        self.control_points_list[new_bezier_curve_name] = [user_control_point_values, user_curve_opacity_alpha_value]
        new_bezier_curve = PathPatch(Path(user_control_point_values, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), transform = self.axes.transData)
        self.bezier_curves[new_bezier_curve_name] = new_bezier_curve

        # Adds a new curve into the Curve_box comboBox and draws the new Bezier curve onto the graph. 
        self.Curve_box.addItem(new_bezier_curve_name)
        self.axes.add_patch(new_bezier_curve)
        self.canvas.draw()

        # Activates the 'Set Curve' and 'Remove Curve' buttons if the user previously had no Bezier curves before pressing the 'Add Curve' button and
        # deletes the 'No Curves' item in the Curve_box comboBox.
        if self.Curve_box.currentText() == 'No Curves':
            self.Curve_box.removeItem(self.Curve_box.currentIndex())
            self.Set_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)

        # Sets the text in the Curve_box comboBox to the latest Bezier curve that the user added.
        else:
            self.Curve_box.setCurrentText('Curve ' + str(len(self.control_points_list)))

        # Disables all buttons, line edit fields, combo boxes, and the spin box until the user chooses which areas of the projection screen to fill if the user adds
        # a Bezier curve that is considered a line.
        if curve_type == 'line':
            self.enableFillLineButtons(line_name = self.Curve_box.currentText(), new_control_points = user_control_point_values, opacity_alpha_value = user_curve_opacity_alpha_value)

        self.SendInfo()

    ## Determines whether the values in the line edit fields consist of only numbered key inputs.
    def evaluateLineEditFields(self):

        user_control_point_values = [self.control_point_1_x_line.text(), self.control_point_2_x_line.text(), 
                                     self.control_point_3_x_line.text(), self.control_point_4_x_line.text(), 
                                     self.control_point_1_y_line.text(), self.control_point_2_y_line.text(), 
                                     self.control_point_3_y_line.text(), self.control_point_4_y_line.text()]

        # Outputs an error message box to the user if one of the user's inputs contains any values other than numbered key inputs.
        for control_point_value in user_control_point_values:
            if re.fullmatch("[-]?[0-9]+[.]?[0-9]*", str(control_point_value)) == None:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Invalid control point values! Values for control points cannot include letters, symbols, or spaces.')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'

        return 'Valid'

    ## Determines whether the user's control points fall under the rules for each Bezier curve type.
    def evaluateControlPoints(self, user_control_point_values, curve_type):  

        # Outputs an error message box to the user if all of the user's control points are on the same coordinate.
        if len(set(user_control_point_values)) == 1:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Invalid control points! All four control points cannot be on the same coordinate.')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'  
        
        # Specifies the conditions for valid control points for Bezier curves that are considered as curves.
        if curve_type == 'curve':

            # Outputs an error message box to the user if the user's inputs for control points 1 and 4 are on same coordinate
            # and the user's inputs for controls 2 and 3 are on the same coordinate for Bezier curves that are considered as curves.
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
            
        # Specifies the conditions for valid control points for Bezier curves that are considered as lines.
        else:    

            # Outputs an error message to the user if the user's inputs for control points 1 and 4 are on the same coordinates for Bezier curves
            # that are considered as lines.
            if user_control_point_values[0][0] == user_control_point_values[3][0] and user_control_point_values[0][1] == user_control_point_values[3][1]:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Control points 1 and 4 cannot be on the same coordinate for lines!')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'

            # Evaluates whether either control points 1 and 4 are within the blue dashed lines.
            if (not (user_control_point_values[0][0] < 0 or user_control_point_values[0][0] > self.window_width or user_control_point_values[0][1] < 0 or user_control_point_values[0][1] > self.window_height)
                and not (user_control_point_values[3][0] < 0 or user_control_point_values[3][0] > self.window_width or user_control_point_values[3][1] < 0 or user_control_point_values[3][1] > self.window_height)):
                
                # Outputs an error message to the user if neither of the user's inputs for control points 1 or 4 are on the blue dashed lines.
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
                
            # Outputs an error message box to the user if the user's inputs for either control points 1 and 4 are not within the blue dashed lines.
            else:
                failedMessageBox = QMessageBox()
                failedMessageBox.setWindowTitle('Mask Feed and Geometry Editing Error - Planetarium Edge Blend')
                failedMessageBox.setText('Control Points 1 or 4 are NOT within blue dashed lines!')
                failedMessageBox.setStandardButtons(QMessageBox.Ok)
                failedMessageBox.exec()
                return 'Invalid'
            
    ## Returns a list of xy coordinates and a single opacity number by converting all of the values in the line edit fields and the spin box.
    def convertUserInputsForCurve(self):
        
        # Creates a list of xy coordinates by converting each value from the line edit fields into a float and pairing each x and y value with its corresponding
        # control point.
        user_control_point_values =  [(float(self.control_point_1_x_line.text()), float(self.control_point_1_y_line.text())), 
                                      (float(self.control_point_2_x_line.text()), float(self.control_point_2_y_line.text())), 
                                      (float(self.control_point_3_x_line.text()), float(self.control_point_3_y_line.text())),
                                      (float(self.control_point_4_x_line.text()), float(self.control_point_4_y_line.text()))]

        # Converts the opacity percentage for the Bezier curve that the user has select in the Curve_box comboBox into a decimal number.
        user_curve_opacity_alpha_value = round(float(self.Curve_opacity_box.cleanText()) / 100, 2)

        return user_control_point_values, user_curve_opacity_alpha_value
        
    ## Enables buttons under the 'Settings for Filling Area for Lines' label based on the user's control points
    #  and disables all of the widgets related to Bezier curves, selecting client servers, and switching back to the main window
    #  for the 'Mask Feed and Geometry Editing' window.
    #  @param line_name The curve name of a user-created Bezier curve that is considered a line under Bezier logic
    #  @param new_control_points The control points of a user-created Bezier curve that is considered a line under Bezier logic
    #  @param opacity_alpha_value The opacity alpha value of a user-created Bezier curve that is considered a line under Bezier logic
    def enableFillLineButtons(self, line_name, new_control_points, opacity_alpha_value):

        # Disables the comboBoxes and spin box.
        self.Client_projectors_box.setEnabled(False)
        self.Curve_box.setEnabled(False)
        self.Curve_opacity_box.setEnabled(False)

        # Disables the 'Line Mode' button and resets its counter.
        self.Line_mode_btn.setEnabled(False)
        self.line_mode_on = False
        self.line_mode_click_count_parity = 0

        # Disables the control point buttons and the mouse cursor functionality for the graph. 
        # Also resets the counter for the control point buttons.
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

        # Disables the line edit fields for the control points.
        self.control_point_1_x_line.setEnabled(False)
        self.control_point_1_y_line.setEnabled(False)
        self.control_point_2_x_line.setEnabled(False)
        self.control_point_2_y_line.setEnabled(False)
        self.control_point_3_x_line.setEnabled(False)
        self.control_point_3_y_line.setEnabled(False)
        self.control_point_4_x_line.setEnabled(False)
        self.control_point_4_y_line.setEnabled(False)

        # Disables the ability to edit, add, and remove Bezier curves on the mask graph.
        self.Set_curve_btn.setEnabled(False)
        self.Add_curve_btn.setEnabled(False)
        self.Remove_curve_btn.setEnabled(False)

        # Disables the 'Back' button to keep the user on the 'Mask Feed and Geometry Editing' window.
        self.Back_btn.setEnabled(False)

        self.line_control_point_name = line_name
        self.line_control_point_1 = new_control_points[0]
        self.line_control_point_4 = new_control_points[3]
        self.line_opacity_alpha_value = opacity_alpha_value

        # Disables the 'Above Line' and 'Below Line' buttons if the user's inputs for control points 1 and 4 are at the same height.
        if self.line_control_point_1[1] == self.line_control_point_4[1]:
            self.Left_line_btn.setEnabled(False)
            self.Right_line_btn.setEnabled(False)
            self.Above_line_btn.setEnabled(True)
            self.Below_line_btn.setEnabled(True)

        # Disables the 'Left of Line' and 'Right of Line' buttons if the user's inputs for control points 1 and 4 are at the same width.
        elif self.line_control_point_1[0] == self.line_control_point_4[0]:
            self.Left_line_btn.setEnabled(True)
            self.Right_line_btn.setEnabled(True)
            self.Above_line_btn.setEnabled(False)
            self.Below_line_btn.setEnabled(False)
        
        # Enables all buttons under the 'Settings for Filling Area for Lines' label if the user's inputs for control points 1 and 4 are not at the same height and width/.
        else:
            self.Left_line_btn.setEnabled(True)
            self.Right_line_btn.setEnabled(True)
            self.Above_line_btn.setEnabled(True)
            self.Below_line_btn.setEnabled(True)
    
    ## Creates a list of xy coordinates for filling in the area between the left side of the projection screen and a user-created Bezier curve that considered a line
    #  once the user presses on the 'Left of Line' button. 
    def fillLineAreaLeft(self):

        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 1 are on the bottom horizontal
        # blue dashed line.
        if self.line_control_point_1[1] == 0:  
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, 0.0)]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 4 are on the bottom horizontal
        # blue dashed line.                                        
        elif self.line_control_point_4[1] == 0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, 0.0)]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 1 are on the top horizontal
        # blue dashed line.
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, float(self.window_height))]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 4 are on the top horizontal
        # blue dashed line.
        elif self.line_control_point_4[1] == float(self.window_height):
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, float(self.window_height))]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 1 are on the left vertical
        # blue dashed line.
        elif self.line_control_point_1[0] == 0:
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 4 are on the left vertical
        # blue dashed line.
        elif self.line_control_point_4[0] == 0:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 1 are on the right vertical
        # blue dashed line.
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(0.0, self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_4[1]), 
                                        (0.0, self.line_control_point_1[1])]
        
        # Makes the control points for filling the area to the left of a user-created Bezier curve if user's inputs for control point 4 are on the right vertical
        # blue dashed line.
        else:
            control_points_line_area = [(0.0, self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_1[1]), 
                                        (0.0, self.line_control_point_4[1])]
        
        self.makeFillArea(control_points_line_area)
        self.SendInfo()
            
    ## Creates a list of xy coordinates for filling in the area between the right side of the projection screen and a user-created Bezier curve that considered a line
    #  once the user presses on the 'Right of Line' button.
    def fillLineAreaRight(self):
        
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 1 are on the bottom horizontal
        # blue dashed line.
        if self.line_control_point_1[1] == 0:
            control_points_line_area = [(float(self.window_width), 0.0),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (float(self.window_width), 0.0)]   
        
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 4 are on the bottom horizontal
        # blue dashed line.
        elif self.line_control_point_4[1] == 0: 
            control_points_line_area = [(float(self.window_width), 0.0),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), 0.0)]   

        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 1 are on the top horizontal
        # blue dashed line.   
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]), 
                                        (float(self.window_width), float(self.window_height))]
            
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 4 are on the top horizontal
        # blue dashed line.
        elif self.line_control_point_4[1] == float(self.window_height):
            control_points_line_area = [(float(self.window_width), float(self.window_height)),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), float(self.window_height))]    
            
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 1 are on the left vertical 
        # blue dashed line.
        elif self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(float(self.window_width), self.line_control_point_1[1]),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (float(self.window_width), self.line_control_point_1[1])] 
            
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 4 are on the left vertical 
        # blue dashed line.
        elif self.line_control_point_4[0] == 0.0:
            control_points_line_area = [(float(self.window_width), self.line_control_point_4[1]),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (float(self.window_width), self.line_control_point_4[1])] 

        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 1 are on the right vertical 
        # blue dashed line. 
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]),  
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (float(self.window_width), self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]  
        
        # Makes the control points for filling the area to the right of a user-created Bezier curve if user's inputs for control point 4 are on the right vertical
        # blue dashed line. 
        else:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]),  
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (float(self.window_width), self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])] 
            
        self.makeFillArea(control_points_line_area)
        self.SendInfo()

    ## Creates a list of xy coordinates for filling in the area between the top side of the projection screen and a user-created Bezier curve that considered a line
    #  once the user presses on the 'Above Line' button.
    def fillLineAreaAbove(self):

        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 1 are on the left vertical 
        # blue dashed line.
        if self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (0.0, float(self.window_height))]
            
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 4 are on the left vertical 
        # blue dashed line.
        elif self.line_control_point_4[0] == 0.0:
            control_points_line_area = [(0.0, float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (0.0, float(self.window_height))]
            
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 1 are on the right vertical 
        # blue dashed line.
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (float(self.window_width), float(self.window_height))]
            
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 4 are on the right vertical 
        # blue dashed line.
        elif self.line_control_point_4[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), float(self.window_height)), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (float(self.window_width), float(self.window_height))]
        
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 1 are on the bottom horizontal 
        # blue dashed line.
        elif self.line_control_point_1[1] == 0.0:
            control_points_line_area = [(self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_1[0], float(self.window_height))]
            
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 4 are on the bottom horizontal 
        # blue dashed line.
        elif self.line_control_point_4[1] == 0.0:
            control_points_line_area = [(self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_4[0], float(self.window_height))]
            
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 1 are on the top horizontal 
        # blue dashed line.
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], float(self.window_height)),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        
        # Makes the control points for filling the area above a user-created Bezier curve if user's inputs for control point 4 are on the top horizontal 
        # blue dashed line.
        else:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], float(self.window_height)),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]

        self.makeFillArea(control_points_line_area)
        self.SendInfo()

    ## Creates a list of xy coordinates for filling in the area between the bottom side of the projection screen and a user-created Bezier curve that considered a line
    #  once the user presses on the 'Below Line' button.
    def fillLineAreaBelow(self):

        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 1 are on the left vertical
        # blue dashed line.
        if self.line_control_point_1[0] == 0.0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], 0.0),
                                        (0.0, 0.0)]
            
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 4 are on the left vertical
        # blue dashed line.
        elif self.line_control_point_4[0] == 0.0:
            control_points_line_area = [(0.0, 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], 0.0),
                                        (0.0, 0.0)]
            
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 1 are on the right vertical
        # blue dashed line.
        elif self.line_control_point_1[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], 0.0),
                                        (float(self.window_width), 0.0)]
        
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 4 are on the right vertical
        # blue dashed line.
        elif self.line_control_point_4[0] == float(self.window_width):
            control_points_line_area = [(float(self.window_width), 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], 0.0),
                                        (float(self.window_width), 0.0)]
        
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 1 are on the bottom horizontal
        # blue dashed line.
        elif self.line_control_point_1[1] == 0.0:
            control_points_line_area = [(self.line_control_point_1[0], self.line_control_point_1[1]), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], 0.0),
                                        (self.line_control_point_1[0], self.line_control_point_1[1])]
        
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 4 are on the bottom horizontal
        # blue dashed line.
        elif self.line_control_point_4[1] == 0.0:
            control_points_line_area = [(self.line_control_point_4[0], self.line_control_point_4[1]), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], 0.0),
                                        (self.line_control_point_4[0], self.line_control_point_4[1])]    

        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 1 are on the top horizontal
        # blue dashed line.
        elif self.line_control_point_1[1] == float(self.window_height):
            control_points_line_area = [(self.line_control_point_1[0], 0.0), 
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_4[0], 0.0),
                                        (self.line_control_point_1[0], 0.0)]
            
        # Makes the control points for filling the area below a user-created Bezier curve if user's inputs for control point 4 are on the top horizontal
        # blue dashed line.
        else:
            control_points_line_area = [(self.line_control_point_4[0], 0.0), 
                                        (self.line_control_point_4[0], self.line_control_point_4[1]),
                                        (self.line_control_point_1[0], self.line_control_point_1[1]),
                                        (self.line_control_point_1[0], 0.0),
                                        (self.line_control_point_4[0], 0.0)]  
        
        self.makeFillArea(control_points_line_area)
        self.SendInfo()
            
    ## Adds a list of xy coordinates to the line_area_points dictionary and adds a PathPatch object to the line_area_shapes dictionary in order to
    #  plot and fill in the area between one of the sides of the projection screen and a user-created Bezier curve that is considered a line.
    #  @param control_points_line_area The control points for filling in an area between one of the sides of the projection screen and a user-created Bezier curve that is considered a line 
    def makeFillArea(self, control_points_line_area):

            # Disables all of the buttons under the 'Settings for Filling Area for Lines' label.
            self.Left_line_btn.setEnabled(False)
            self.Right_line_btn.setEnabled(False)
            self.Above_line_btn.setEnabled(False)
            self.Below_line_btn.setEnabled(False)

            # Updates the line_area_points and line_area_shapes dictionaries based on the list of xy coordinates for filling in an area of the projection screen
            # through a user-created Bezier curve that is considered a line.
            self.line_area_points[self.line_control_point_name] = [control_points_line_area, self.line_opacity_alpha_value]
            self.line_area_shapes[self.line_control_point_name] = PathPatch(Path(control_points_line_area, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), transform=self.axes.transData)

            # Redraws the canvas in order to show the line area shape that was created by the user.  
            self.redrawCanvas()

            # Reactivates all of the buttons related to Bezier curves, client servers, and switching windows within the GUI. 
            self.Client_projectors_box.setEnabled(True)
            self.Curve_box.setEnabled(True)
            self.Curve_opacity_box.setEnabled(True)

            self.Line_mode_btn.setEnabled(True)

            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)

            self.control_point_1_x_line.setEnabled(True)
            self.control_point_1_y_line.setEnabled(True)
            self.control_point_2_x_line.setEnabled(True)
            self.control_point_2_y_line.setEnabled(True)
            self.control_point_3_x_line.setEnabled(True)
            self.control_point_3_y_line.setEnabled(True)
            self.control_point_4_x_line.setEnabled(True)
            self.control_point_4_y_line.setEnabled(True)

            self.Set_curve_btn.setEnabled(True)
            self.Add_curve_btn.setEnabled(True)
            self.Remove_curve_btn.setEnabled(True)

            self.Back_btn.setEnabled(True)

    ## Deletes the Bezier curve that the user has select in the Curve_box comboBox and updates the names of all curves after the Bezier curve that the user has selected.
    #  This happens once the user presses the 'Remove curve' button.
    def removeCurve(self):

        # Saves the number and name of the Bezier curve that the user has select in the Curve_box comboBox to remove.
        removed_curve_number = int(str.split(self.Curve_box.currentText(), ' ')[1])
        removed_curve_name = self.Curve_box.currentText()

        # Saves the number of user-created Bezier curves before removing the Bezier curve.
        total_curves_before_removal = len(self.bezier_curves)

        # Updates the names of Bezier curves that are after the Bezier curve that the user has select in the Curve_box comboBox to remove.
        # This happens only if the user chooses to remove a Bezier curve that is not at the end of the dictionaries.
        if removed_curve_number < total_curves_before_removal:
            changed_curves = []
            index = removed_curve_number + 1

            # Creates a list of new curve names for all Bezier curves that are after the Bezier curve that the user has select in the Curve_box comboBox to remove.
            while index <= total_curves_before_removal:
                changed_curves.append('Curve ' + str(index))
                index = index + 1

            # Removes the Bezier curve from all dictionaries if the Bezier curve that the user has select in the Curve_box comboBox to remove is considered a line under Bezier logic.
            if removed_curve_name in self.line_area_points and len(self.line_area_points) == 1 and len(self.control_points_list) == 1:
                del self.control_points_list[removed_curve_name]
                del self.bezier_curves[removed_curve_name]
                del self.line_area_points[removed_curve_name]
                del self.line_area_shapes[removed_curve_name]

            else:
                # Iterates through the list of new curve names.
                for changed_curve in changed_curves:
                    new_curve_number = int(str.split(changed_curve, ' ')[1]) - 1

                    # Deletes a Bezier curve from all dictionaries if its new curve number matches the curve number that Bezier curve that the user has selected
                    # to remove and if the Bezier curve is considered a line under Bezier logic.
                    if new_curve_number == removed_curve_number:
                        if removed_curve_name in self.line_area_points:
                            del self.control_points_list[removed_curve_name]
                            del self.bezier_curves[removed_curve_name]
                            del self.line_area_points[removed_curve_name]
                            del self.line_area_shapes[removed_curve_name]
                    
                    # Moves each value within the dictionaries to the previous key within the dictionaries.
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

        # Removes the Bezier curve at the end of the dictionaries if the user has select in the Curve_box comboBox to remove this Bezier curve.
        else:
            del self.control_points_list[self.Curve_box.currentText()]
            del self.bezier_curves[self.Curve_box.currentText()]

            if self.Curve_box.currentText() in self.line_area_points:
                del self.line_area_points[self.Curve_box.currentText()]
                del self.line_area_shapes[self.Curve_box.currentText()]

            # Creates a new item on the comboBox list and deactivates the 'Set curve' and 'Remove curve' buttons 
            # if the user removes the only Bezier curve left in the dictionaries.
            if not self.bezier_curves.keys():
                self.Curve_box.addItem('No Curves')

                self.Set_curve_btn.setEnabled(False)
                self.Remove_curve_btn.setEnabled(False)

            self.Curve_box.removeItem(self.Curve_box.currentIndex())
        
        self.redrawCanvas()
        self.SendInfo()

    ## Sets the values of the line edit fields and the curve opacity spin box to the Bezier curve that the user has select in the Curve_box comboBox anytime the value
    #  within Curve_box comboBox changes.    
    def selectedCurveChanged(self):

        # Does not set the values of the line edit fields and the curve opacity spin box if there is not a curve under the Curve_box spin box.
        if self.Curve_box.currentText() == 'No Curves' or self.Curve_box.currentText() == '':
            return

        # Sets the line edit fields and curve opacity based on the curve that the Curve_box comboBox changed into.
        # This also redraws the mask graph.
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

    ## Enables and disables mouse cursor functionality for control point 1 based on how many times the user has pressed on the 'Control Point 1' button. 
    def controlPoint1Clicked(self):
        
        self.control_point_1_click_count_parity = self.control_point_1_click_count_parity + 1

        # Reanables Control Points 2, 3, and 4 buttons and resets the counter for the number of times that the 'Control Point 1' butotn has been clicked
        # if the user has pressed on the 'Control Point 1' button twice. 
        if self.control_point_1_click_count_parity % 2 == 0:            
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)
            self.control_point_1_click_cursor_enable = False
            self.control_point_1_click_count_parity == 0

        # Disables Control Points 2, 3, and 4 buttons if the user has only clicked on the 'Control Point 1' button once.
        else:
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_1_click_cursor_enable = True
    
    ## Enables and disables mouse cursor functionality for control point 2 based on how many times the user has pressed on the 'Control Point 2' button. 
    def controlPoint2Clicked(self):

        self.control_point_2_click_count_parity = self.control_point_2_click_count_parity + 1

        # Reanables Control Points 1, 3, 4, and 'Line Mode' buttons and resets the counter for the number of times that the 'Control Point 2' button has been clicked
        # if the user has pressed on the 'Control Point 2' button twice.
        if self.control_point_2_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)
            self.Line_mode_btn.setEnabled(True)
            self.control_point_2_click_cursor_enable = False
            self.control_point_2_click_count_parity == 0

        # Disables Control Points 1, 3, 4, and 'Line Mode' buttons if the user has only clicked on the 'Control Point 2' button once.
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_2_click_cursor_enable = True

            self.Line_mode_btn.setEnabled(False)
            self.line_mode_on = False
            self.line_mode_click_count_parity = 0
            
    ## Enables and disables mouse cursor functionality for control point 3 based on how many times the user has pressed on the 'Control Point 3' button. 
    def controlPoint3Clicked(self):

        self.control_point_3_click_count_parity = self.control_point_3_click_count_parity + 1

        # Reanables Control Points 1, 2, 4, and 'Line Mode' buttons and resets the counter for the number of times that the 'Control Point 3' button has been clicked
        # if the user has pressed on the 'Control Point 3' button twice. 
        if self.control_point_3_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_4_btn.setEnabled(True)  
            self.Line_mode_btn.setEnabled(True)      
            self.control_point_3_click_cursor_enable = False
            self.control_point_3_click_count_parity == 0
        
        # Disables Control Points 1, 2, 4, and 'Line Mode' buttons if the user has only clicked on the 'Control Point 3' button once.
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_4_btn.setEnabled(False)
            self.control_point_3_click_cursor_enable = True

            self.Line_mode_btn.setEnabled(False)
            self.line_mode_on = False
            self.line_mode_click_count_parity = 0
    
    ## Enables and disables mouse cursor functionality for control point 4 based on how many times the user has pressed on the 'Control Point 4' button.  
    def controlPoint4Clicked(self):

        self.control_point_4_click_count_parity = self.control_point_4_click_count_parity + 1

        # Reanables Control Points 1, 2, and 3 buttons and resets the counter for the number of times that the 'Control Point 4' button has been clicked 
        # if the user has pressed on the 'Control Point 4' button twice. 
        if self.control_point_4_click_count_parity % 2 == 0:
            self.Control_point_1_btn.setEnabled(True)
            self.Control_point_2_btn.setEnabled(True)
            self.Control_point_3_btn.setEnabled(True)        
            self.control_point_4_click_cursor_enable = False
            self.control_point_4_click_count_parity == 0

        # Disables Control Points 1, 2, and 3 buttons if the user has only clicked on the 'Control Point 4' button once.
        else:
            self.Control_point_1_btn.setEnabled(False)
            self.Control_point_2_btn.setEnabled(False)
            self.Control_point_3_btn.setEnabled(False)
            self.control_point_4_click_cursor_enable = True

    ## Dictates whether the Bezier curve (and its associated line area shape if it exists) that the user has select in the Curve_box comboBox
    #  appears in a black or red color on the mask graph based on the number of times the user has pressed on the 'Show Selected Curve in Contrasting Color' button.
    def showContrastCurve(self):

        self.contrast_curve_click_count_parity = self.contrast_curve_click_count_parity + 1

        # Makes the Bezier curve (and its associated line area shape if it exists) that the user has select in the Curve_box comboBox 
        # appear in a black color and resets the counter for the number of times that the 'Show Selected Curve in Contrasting Color' button has been clicked
        # if the user has pressed on the 'Show Selected Curve in Contrasting Color' button twice.
        if self.contrast_curve_click_count_parity % 2 == 0:
            self.contrast_curve = False
            self.contrast_curve_click_count_parity = 0

        # Makes the Bezier curve (and its associated line area shape if it exists) that the user has select in the Curve_box comboBox 
        # appear in a red color if the user has only pressed on the 'Show Selected Curve in Contrasting Color' button once.
        else:
            self.contrast_curve = True

        self.redrawCanvas()

    ## Dictates whether the areas of the Bezier curves and the line area shapes appear on the mask graph based on how many times the user has pressed the
    # 'Show Areas' button.
    def showAreas(self):

        self.show_areas_click_count_parity = self.show_areas_click_count_parity + 1

        # Makes the area of Bezier curves and line area shapes visible to the user and resets the counter for the number of times the 'Show Areas' button
        # has been clicked if the user has clicked on the 'Show Areas' button twice.
        if self.show_areas_click_count_parity % 2 == 0:
            self.show_areas = False
            self.show_areas_click_count_parity = 0

        # Makes the area of Bezier curves and line area shapes nonvisible to the user if the user has only clicked on the 'Show Areas' button once.
        else:
            self.show_areas = True
        self.redrawCanvas()
    
    ## Dictates whether the control points of the Bezier curve that the user has selected in the Curve_box comboBox appears in a red color on the mask graph
    #  based on how many times the user has pressed on the 'Show Control Points' button.
    def showControlPoints(self):

        self.show_control_points_click_count_parity = self.show_control_points_click_count_parity + 1

        # Makes the control points of the Bezier curve that the user has selected in the Curve_box comboBox appear in a red color and resets the counter
        # for the number of times the user has clicked on the 'Show Control Points' button if the user has pressed on the 'show Control Points' button twice.
        if self.show_control_points_click_count_parity % 2 == 0:
            self.show_control_points = False
            self.show_control_points_click_count_parity = 0
        
        # Makes the control points of the Bezier curve that the user has selected in the Curve_box comboBox nonvisible to the user.
        else:
            self.show_control_points = True
        self.redrawCanvas()
    
    ##  Puts the xy coordinates that the user clicked on within the mask graph to the line edit fields of the control point button that the user has clicked on.
    #   @param cursor_x The x coordinate of the user's mouse cursor
    #   @param cursor_y The y coordinate of the user's mouse cursor
    #   @param x_line_edit The x line edit field of the control point button that the user has clicked on
    #   @param x_line_edit The y line edit field of the control point button that the user has clicked on
    def setMouseCursorCoordinates(self, cursor_x, cursor_y, x_line_edit, y_line_edit):
        
        # Checks if the user's mouse cursor was on the mask graph when the user clicked on the left mouse button with mouse cursor functionality turned on.
        if cursor_x != None and cursor_y != None:

            # Rounds the user's mouse cursor xy coordinates to the closest blue dashed line if the user clicked close enough to 
            # one of the borders of the projection screen. 
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

            # Rounds the user's mouse cursor by two decimal places if the user did not click near the borders of the projection screen.
            else:
                x_line_edit.setText(str(round(cursor_x, 2)))
                y_line_edit.setText(str(round(cursor_y, 2)))

    ## Handles the mouse cursor functionality for editting Bezier curves once the user has clicked on one of the four control point buttons. 
    def leftMouseClicked(self, event):

        # Takes the xy coordinates of the user's mouse cursor if the user presses on the left nouse button.
        if event.button == MouseButton.LEFT:

            # Handles the mouse cursor functionality for the 'Control Point 1' button.
            if self.control_point_1_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_1_x_line, self.control_point_1_y_line)
                self.setCurve()

            # Handles the mouse cursor functionality for the 'Control Point 2' button.
            elif self.control_point_2_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_2_x_line, self.control_point_2_y_line)
                self.setCurve()

            # Handles the mouse cursor functionality for the 'Control Point 3' button.
            elif self.control_point_3_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_3_x_line, self.control_point_3_y_line)
                self.setCurve()
            
            # Handles the mouse cursor functionality for the 'Control Point 4' button.
            elif self.control_point_4_click_cursor_enable:
                self.setMouseCursorCoordinates(event.xdata, event.ydata, self.control_point_4_x_line, self.control_point_4_y_line)
                self.setCurve()

    ## Dictates whether to enable or disable the ability to make control points 2 and 3 equal to control point 1 based on how many times the user
    #  presses on the 'Line Mode' button.
    def lineModeClicked(self):
        
        self.line_mode_click_count_parity = self.line_mode_click_count_parity + 1

        # Enables the line edit fields for control points 2 and 3, resets line mode to be off, and resets the counter for the number of times 'Line Mode'
        # has been clicked if the user clicks on the 'Line Mode' button twice.
        if self.line_mode_click_count_parity % 2 == 0:
            self.control_point_2_x_line.setEnabled(True)
            self.control_point_2_y_line.setEnabled(True)

            self.control_point_3_x_line.setEnabled(True)
            self.control_point_3_y_line.setEnabled(True)

            self.line_mode_on = False
            self.line_mode_click_count_parity = 0

            # Disables the control points 2 and 3 buttons if the user still has either the 'Control Point 1' or 'Control Point 4' buttons to be on.
            if self.control_point_1_click_cursor_enable or self.control_point_4_click_cursor_enable:
                self.Control_point_2_btn.setEnabled(False)
                self.Control_point_3_btn.setEnabled(False)

            # Enables the control points 2 and 3 buttons if the user still has neither the 'Control Point 1' or 'Control Point 4' buttons to be on.
            else:
                self.Control_point_2_btn.setEnabled(True)
                self.Control_point_3_btn.setEnabled(True)

        # Disables the buttons and line edit fields for control points 2 and 3 and sets the line edit fields of control points 2 and 3 equal to the
        # line edit fields of control point 1 if the user has only clicked on the 'Line Mode' button once.
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

    ## Sets the x line edit fields of Control Points 2 and 3 equal to the x line edit field of Control Point 1 if the user has clicked
    #  on the 'Line Mode' button to be on and the value within the x line edit field of Control Point 1 changes.
    def controlPoint1XChanged(self):
        if self.line_mode_on == True:
            self.control_point_2_x_line.setText(self.control_point_1_x_line.text())
            self.control_point_3_x_line.setText(self.control_point_1_x_line.text())

    ## Sets the y line edit fields of Control Points 2 and 3 equal to the y line edit field ofControl Point 1 if the user has clicked
    #  on the 'Line Mode' button to be on and the value within the y line edit field of Control Point 1 changes.
    def controlPoint1YChanged(self):
        if self.line_mode_on == True:
            self.control_point_2_y_line.setText(self.control_point_1_y_line.text())
            self.control_point_3_y_line.setText(self.control_point_1_y_line.text())

    ## Client combo box text changed signal
    # Checks whether the client combo box was changed and updates the Bezier info from that particular client
    def clientComboBoxChanged(self):
        # Resets the axes and curves
        self.axes.clear()
        self.bezier_curves.clear()
        self.line_area_shapes.clear()

        # Resets the line mode
        self.line_mode_on = False
        self.line_mode_click_count_parity = 0

        # Attempt to connect to the new client to retrieve Bezier information.
        try:
            self.GetInfo()

            # If successful, reset the buttons to enabled as they may have been disabled if the previously selected client was not connected.
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

            # Sets the Bezier curves according to the bezer information retrieved.
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
                self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')

        # If unable to connect to the selected client, set buttons to disabled to ensure user is not able to change curves for an unconnected client.
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
            
            # Display an error message indicating the client is not connected.
            errorBox = QMessageBox()
            errorBox.setWindowTitle('Connection Error - Planetarium Edge Blend')
            errorBox.setText("Client at IP Address not found. Are you sure the client application is running on it?")
            errorBox.exec()

            self.axes.set_title('Not connected to ' + self.Client_projectors_box.currentText())
        
        # Reset the curve combo box
        self.Curve_box.clear()
        self.Curve_box.addItems(list(self.bezier_curves.keys()))

        # Set the text boxes to the new Bezier information
        self.setTextBoxes()  
        
        # Redraw the canvas.
        self.axes.set_xlim((0 - self.boundary_size, self.window_width + self.boundary_size))
        self.axes.set_ylim((0 - self.boundary_size, self.window_height + self.boundary_size))
        self.axes.grid(color = 'k')
        self.canvas.draw() 

    '''
    NETWORKING
    '''

    ## Retrieves Bezier curve information from a given client
    #
    # Uses the Clients combo box (Client_projectors_box) and the client_ip.txt file to get the current client
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

    ## Sends Bezier curve information to a given client
    #
    # Uses the Clients combo box (Client_projectors_box) and the client_IP.txt file to get the current client
    def SendInfo(self):
        ## IP of the currently selected client
        clientIP = self.client_servers_IP_addresses[self.Client_projectors_box.currentText()]

        ## QTcpSocket variable representing the host side connection with the client.
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(clientIP, self.PORT, QIODevice.ReadWrite)
        self.tcpSocket.waitForConnected(5000)

        ## Variable containing Bezier information to send to client
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


'''
# PROJECTOR CONFIGURATION
'''

## Represents the 'Projector Configuration - Planetarium Edge Blend' window for the host GUI.
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
    def listItemClicked(self):
        self.Edit_name.setEnabled(True)
        self.Edit_IP.setEnabled(True)
        self.Edit_btn.setEnabled(True)
        self.Delete_btn.setEnabled(True)
        self.Edit_name.setText(self.Client_list.currentItem().text().split('-')[0])
        self.Edit_IP.setText(self.Client_list.currentItem().text().split('-')[1])
        
    ## This function adds a client to the client_ip.txt file
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
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
