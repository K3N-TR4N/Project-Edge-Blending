from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backend_bases import MouseButton

import re

import matplotlib
import matplotlib.pyplot as plt        
matplotlib.use('Qt5Agg')

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        #######################################################

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

      #######################################################

        MainWindow.setObjectName("Geometry Editing - Planaterarium Edge")
        MainWindow.resize(self.window_width, self.window_height)
        
        #######################################################

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_1 = QtWidgets.QFrame(self.centralwidget)
        self.frame_1.setGeometry(QtCore.QRect(20, 40, 821, 581))
        self.frame_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_1.setObjectName("frame_1")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.frame_1)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 50, 821, 481))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")

        #####################################################################

        # Create a figure and axis objects
        figure, self.axes = plt.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        control_points_1 = [(float(0 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height)), (float(0 * self.window_width), float(1 * self.window_height))]
        control_points_2 = [(float(0 * self.window_width), float(1 * self.window_height)), (float(0.5 * self.window_width), float(0 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        control_points_3 = [(float(1 * self.window_width), float(0 * self.window_height)), (float(0.5 * self.window_width), float(0.5 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height)), (float(1 * self.window_width), float(1 * self.window_height))]
        
        initial_sets_of_control_points = [control_points_1, control_points_2, control_points_3]

        self.control_points_list = {}
        self.bezier_curves = {}
        self.line_areas = {}

        self.index = 0

        #'''
        for control_points in initial_sets_of_control_points:
            self.index = self.index + 1
            self.control_points_list['Curve ' + str(self.index)] = control_points
            self.bezier_curves['Curve ' + str(self.index)] = PathPatch(Path(control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)
            
        for curve in self.bezier_curves:
            self.axes.add_patch(self.bezier_curves[curve])
        #'''

        self.cid = plt.connect('button_press_event', self.leftMouseClicked)

        # Set parameters of the graph to be 1920x1080
        plt.xlim(0, 1920)
        plt.ylim(0, 1080)
        #manager = plt.get_current_fig_manager()
        #manager.full_screen_toggle()



        #HERE#
        self.horizontalLayout_1.addWidget(self.canvas)

        #####################################################################

        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(870, 90, 331, 481))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 331, 221))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_1.setObjectName("verticalLayout_1")
        self.comboBox_1 = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox_1.setObjectName("comboBox_1")
        self.verticalLayout_1.addWidget(self.comboBox_1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridLayout_4.addWidget(self.lineEdit_6, 2, 2, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_4.addWidget(self.comboBox_2, 0, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_4.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_4.addWidget(self.pushButton_6, 4, 0, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout_4.addWidget(self.lineEdit_5, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 0, 2, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_4.addWidget(self.pushButton_4, 2, 0, 1, 1)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout_4.addWidget(self.lineEdit_7, 3, 2, 1, 1)
        self.label_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_1.setObjectName("label_1")
        self.gridLayout_4.addWidget(self.label_1, 0, 1, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_4.addWidget(self.lineEdit_3, 3, 1, 1, 1)
        self.lineEdit_1 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.gridLayout_4.addWidget(self.lineEdit_1, 1, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_4.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_4.addWidget(self.pushButton_5, 3, 0, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_4.addWidget(self.pushButton_7, 5, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_4.addWidget(self.pushButton_2, 5, 2, 1, 1)
        self.pushButton_1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_1.setObjectName("pushButton_1")
        self.gridLayout_4.addWidget(self.pushButton_1, 5, 1, 1, 1)
        self.lineEdit_8 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.gridLayout_4.addWidget(self.lineEdit_8, 4, 2, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout_4.addWidget(self.lineEdit_4, 4, 1, 1, 1)
        self.verticalLayout_1.addLayout(self.gridLayout_4)

        #########################################################################

        if not self.bezier_curves.keys():
            self.comboBox_2.addItem('No Curves')
        else:
            self.comboBox_2.addItems(list(self.bezier_curves.keys()))
            
            first_curve_control_points = self.control_points_list[self.comboBox_2.currentText()]

            self.lineEdit_1.setText(str(first_curve_control_points[0][0]))
            self.lineEdit_5.setText(str(first_curve_control_points[0][1]))
            self.lineEdit_2.setText(str(first_curve_control_points[1][0]))
            self.lineEdit_6.setText(str(first_curve_control_points[1][1]))
            self.lineEdit_3.setText(str(first_curve_control_points[2][0]))
            self.lineEdit_7.setText(str(first_curve_control_points[2][1]))
            self.lineEdit_4.setText(str(first_curve_control_points[3][0]))
            self.lineEdit_8.setText(str(first_curve_control_points[3][1]))
            #HERE#
            self.redrawCanvas()
        
        self.comboBox_2.currentTextChanged.connect(self.selectedCurveChanged)

        self.pushButton_1.clicked.connect(self.addNewCurveClicked)
        self.pushButton_2.clicked.connect(self.removeCurveClicked)
        self.pushButton_3.clicked.connect(self.controlPoint1Clicked)
        self.pushButton_4.clicked.connect(self.controlPoint2Clicked)
        self.pushButton_5.clicked.connect(self.controlPoint3Clicked)
        self.pushButton_6.clicked.connect(self.controlPoint4Clicked)
        self.pushButton_7.clicked.connect(self.setControlPoints)

        #########################################################################

        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.frame_2)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, 260, 331, 92))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_8 = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_5.addWidget(self.pushButton_8, 0, 0, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout_5.addWidget(self.pushButton_9, 0, 1, 1, 1)
        self.pushButton_10 = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout_5.addWidget(self.pushButton_10, 1, 0, 1, 1)
        self.pushButton_11 = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_11.setObjectName("pushButton_11")
        self.gridLayout_5.addWidget(self.pushButton_11, 1, 1, 1, 1)

        ###########################################################################

        self.pushButton_8.clicked.connect(self.fillLineAreaLeft)
        self.pushButton_9.clicked.connect(self.fillLineAreaRight)
        self.pushButton_10.clicked.connect(self.fillLineAreaAbove)
        self.pushButton_11.clicked.connect(self.fillLineAreaBelow)

        self.pushButton_8.setEnabled(False)
        self.pushButton_9.setEnabled(False)
        self.pushButton_10.setEnabled(False)
        self.pushButton_11.setEnabled(False)

        ###########################################################################

        self.verticalLayout_2.addLayout(self.gridLayout_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.frame_2)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(0, 390, 331, 92))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.pushButton_12 = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.pushButton_12.setObjectName("pushButton_12")
        self.verticalLayout_3.addWidget(self.pushButton_12)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_13 = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.pushButton_13.setObjectName("pushButton_13")
        self.horizontalLayout_4.addWidget(self.pushButton_13)
        self.pushButton_14 = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.pushButton_14.setObjectName("pushButton_14")
        self.horizontalLayout_4.addWidget(self.pushButton_14)

        ##########################################################

        self.pushButton_12.clicked.connect(self.contrastCurveClicked)
        self.pushButton_13.clicked.connect(self.showAreas)
        self.pushButton_14.clicked.connect(self.showControlPoints)

        ##########################################################

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

### HERE ###        
        #############################################################################################
        # Shows mask in graph form. NOTE: This must be commented out to save the image or image will not save.  
        #plt.show()

        # Remove the axis spines
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
        figure.set_size_inches(19.2, 10.8)

        # save output as transparent
        plt.savefig('figure.png', transparent = True, dpi=100)

        #############################################################################################

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Geometry Editing - Planetarium Edge Blend"))
        self.pushButton_3.setText(_translate("MainWindow", "Control Point 1"))
        self.pushButton_6.setText(_translate("MainWindow", "Control Point 4"))
        self.label_2.setText(_translate("MainWindow", "Y"))
        self.pushButton_4.setText(_translate("MainWindow", "Control Point 2"))
        self.label_1.setText(_translate("MainWindow", "X"))
        self.pushButton_5.setText(_translate("MainWindow", "Control Point 3"))
        self.pushButton_7.setText(_translate("MainWindow", "Set Control Points"))
        self.pushButton_2.setText(_translate("MainWindow", "Remove curve"))
        self.pushButton_1.setText(_translate("MainWindow", "Add new curve"))
        self.label_3.setText(_translate("MainWindow", "Settings for Filling Area for Lines"))
        self.pushButton_8.setText(_translate("MainWindow", "Left of Line"))
        self.pushButton_9.setText(_translate("MainWindow", "Right of Line"))
        self.pushButton_10.setText(_translate("MainWindow", "Above Line"))
        self.pushButton_11.setText(_translate("MainWindow", "Below Line"))
        self.label_4.setText(_translate("MainWindow", "Mask Display Settings"))
        self.pushButton_12.setText(_translate("MainWindow", "Show Selected Curve In Contrasting Color"))
        self.pushButton_13.setText(_translate("MainWindow", "Show Areas"))
        self.pushButton_14.setText(_translate("MainWindow", "Show Control Points"))
        self.retrieveProjectors()

    ###########################################################

    def retrieveProjectors(self):
        client_servers_info_file = open('projectors.txt', 'r')

        self.client_servers_IP_addresses = []

        for line in client_servers_info_file:
            self.client_servers_IP_addresses.append(line.removesuffix('\n'))

        client_servers_info_file.close()

        self.projector_numbers = []
        self.projector_count = 0

        for projector in self.client_servers_IP_addresses:
            self.projector_count = self.projector_count + 1 
            self.projector_numbers.append('Projector ' + str(self.projector_count) + ' (' + projector + ')')

        self.comboBox_1.addItems(self.projector_numbers)
    
### HERE ###    
    def redrawCanvas(self):
        self.axes.clear()

        #self.axes.plot(self.boundaries_x, self.boundaries_y, linestyle = '--', color = 'b')
        
        if self.comboBox_2.currentText() != 'No Curves' and self.show_control_points == True:
            for control_points in self.control_points_list[self.comboBox_2.currentText()]:
                self.axes.plot(control_points[0], control_points[1], 'ro')
        
        for curve in self.bezier_curves:
            #if curve == self.comboBox_2.currentText() and self.contrast_curve == True and self.show_areas == True:
            #self.bezier_curves[curve].set(edgecolor = 'r', facecolor = 'r')
            #elif curve == self.comboBox_2.currentText() and self.contrast_curve == True and self.show_areas == False:
            #self.bezier_curves[curve].set(edgecolor = 'r', facecolor = 'None')
            #elif curve == self.comboBox_2.currentText() and self.contrast_curve == False and self.show_areas == True:
            self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'k')
            #else:
                #if self.show_areas == True:
            self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'k')
                #else:
            #self.bezier_curves[curve].set(edgecolor = 'k', facecolor = 'None')
            self.axes.add_patch(self.bezier_curves[curve])

        for area in self.line_areas:
            #if area == self.comboBox_2.currentText() and self.contrast_curve == True and self.show_areas == True:
            #self.line_areas[area].set(edgecolor = 'r', facecolor = 'r')
            #elif area == self.comboBox_2.currentText() and self.contrast_curve == True and self.show_areas == False:
            #self.line_areas[area].set(edgecolor = 'r', facecolor = 'None')
            #elif area == self.comboBox_2.currentText() and self.contrast_curve == False and self.show_areas == True:
            self.line_areas[area].set(edgecolor = 'k', facecolor = 'k')
            #else:
                #if self.show_areas == True:
            self.line_areas[area].set(edgecolor = 'k', facecolor = 'k')
                #else:
            self.line_areas[area].set(edgecolor = 'k', facecolor = 'None')
            self.axes.add_patch(self.line_areas[area])
        
        self.axes.set_xlim((0 - self.boundary_size * 3, self.window_width + self.boundary_size * 3))
        self.axes.set_ylim((0 - self.boundary_size * 3, self.window_height + self.boundary_size * 3))
        self.axes.grid(color = 'k')
        #HERE# 
        self.canvas.draw() 

    def setControlPoints(self):      
        if self.comboBox_2.currentText() == 'No Curves':
            return
        else:
            
            if self.evaluateLineEditFields() == 'Valid':
                user_control_point_1_x = float(self.lineEdit_1.text())
                user_control_point_2_x = float(self.lineEdit_2.text())
                user_control_point_3_x = float(self.lineEdit_3.text())
                user_control_point_4_x = float(self.lineEdit_4.text())
                user_control_point_1_y = float(self.lineEdit_5.text())
                user_control_point_2_y = float(self.lineEdit_6.text())
                user_control_point_3_y = float(self.lineEdit_7.text())
                user_control_point_4_y = float(self.lineEdit_8.text())
            else: 
                return
            
            user_control_point_values = [user_control_point_1_x, user_control_point_1_y, 
                                            user_control_point_2_x, user_control_point_2_y, 
                                            user_control_point_3_x, user_control_point_3_y, 
                                            user_control_point_4_x, user_control_point_4_y]

            if self.evaluateControlPoints(user_control_point_values = user_control_point_values) == 'Invalid':
                return

            new_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]
            self.control_points_list[self.comboBox_2.currentText()] = new_control_points
            self.bezier_curves[self.comboBox_2.currentText()] = PathPatch(Path(new_control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none', transform = self.axes.transData)

            if self.comboBox_2.currentText() in self.line_areas:
                del self.line_areas[self.comboBox_2.currentText()]

            self.redrawCanvas()

            self.evaluateLineCurve(line_name = self.comboBox_2.currentText(), new_control_points = new_control_points)
        
    def addNewCurveClicked(self):

        '''
        print('\nBefore new curve')
        print(self.control_points_list)
        '''

        if self.evaluateLineEditFields() == 'Valid':
            user_control_point_1_x = float(self.lineEdit_1.text())
            user_control_point_2_x = float(self.lineEdit_2.text())
            user_control_point_3_x = float(self.lineEdit_3.text())
            user_control_point_4_x = float(self.lineEdit_4.text())
            user_control_point_1_y = float(self.lineEdit_5.text())
            user_control_point_2_y = float(self.lineEdit_6.text())
            user_control_point_3_y = float(self.lineEdit_7.text())
            user_control_point_4_y = float(self.lineEdit_8.text())
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

        self.comboBox_2.addItem(new_bezier_curve_name)
        self.axes.add_patch(new_bezier_curve)
        self.canvas.draw()

        if self.comboBox_2.currentText() == 'No Curves':
            self.comboBox_2.removeItem(self.comboBox_2.currentIndex())
        else:
            self.comboBox_2.setCurrentText('Curve ' + str(len(self.control_points_list)))

        '''
        print('\nAfter new curve')
        print(self.control_points_list)
        '''

        self.evaluateLineCurve(line_name = new_bezier_curve_name, new_control_points = new_control_points)

    def evaluateLineEditFields(self):
        input_status = 'Valid'

        user_control_point_values = [self.lineEdit_1.text(), self.lineEdit_2.text(), 
                                     self.lineEdit_3.text(), self.lineEdit_4.text(), 
                                     self.lineEdit_5.text(), self.lineEdit_6.text(), 
                                     self.lineEdit_7.text(), self.lineEdit_8.text()]

        for control_point_value in user_control_point_values:
            if re.fullmatch("[-]?[0-9]+[.]?[0-9]*", str(control_point_value)) == None:
                print('Invalid control point values! Values for control points cannot include letters, symbols, or spaces.')
                return 'Invalid'

        return input_status

    #   All four control points cannot have the same coordinate
    #   Control Point 1 and Control 4 cannot be at the same point
    #   Control Point 1 and Control 4 have to be on the boundary lines
    def evaluateControlPoints(self, user_control_point_values):
        
        input_status = 'Valid'
        
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
            self.pushButton_1.setEnabled(False)
            self.pushButton_2.setEnabled(False)

            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            
            self.pushButton_7.setEnabled(False)

            self.comboBox_2.setEnabled(False)

            self.line_control_point_name = line_name
            self.line_control_point_1 = new_control_points[0]
            self.line_control_point_4 = new_control_points[3]

            if self.line_control_point_1[1] == self.line_control_point_4[1]:

                if (self.line_control_point_1[0] == 0.0 and self.line_control_point_4[0] == self.window_width) or (self.line_control_point_1[0] == self.window_width and self.line_control_point_4[0] == 0):
                    self.pushButton_8.setEnabled(False)
                    self.pushButton_9.setEnabled(False)
                    self.pushButton_10.setEnabled(True)
                    self.pushButton_11.setEnabled(True)
                else:
                    print('Invalid control points! For horizontal lines, control points 1 and 4 must be on the ends of the projection screen.')
                    
                    self.pushButton_1.setEnabled(True)
                    self.pushButton_2.setEnabled(True)

                    self.pushButton_3.setEnabled(True)
                    self.pushButton_4.setEnabled(True)
                    self.pushButton_5.setEnabled(True)
                    self.pushButton_6.setEnabled(True)

                    self.pushButton_7.setEnabled(True)

                    self.comboBox_2.setEnabled(True)
                    
                    return
            
            else:
                self.pushButton_8.setEnabled(True)
                self.pushButton_9.setEnabled(True)
                self.pushButton_10.setEnabled(False)
                self.pushButton_11.setEnabled(False)

    
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
                
            self.pushButton_8.setEnabled(False)
            self.pushButton_9.setEnabled(False)
            self.pushButton_10.setEnabled(False)
            self.pushButton_11.setEnabled(False)

            self.line_areas[self.line_control_point_name] = PathPatch(Path(control_points_line_area, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]), fc = 'r', transform=self.axes.transData)

            self.redrawCanvas()

            self.pushButton_1.setEnabled(True)
            self.pushButton_2.setEnabled(True)

            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)

            self.pushButton_7.setEnabled(True)

            self.comboBox_2.setEnabled(True)

    def removeCurveClicked(self):

        if self.comboBox_2.currentText() == 'No Curves':
            return
        else:
            '''            
            print('\nBefore new curve')
            print(self.control_points_list)
            print(self.bezier_curves)
            print(self.line_areas)
            '''  
            
            curve_numbers = []
            
            '''
            for index in range(self.index):
                curve_numbers.append(str(index + 1))

            print('\n')
            print(curve_numbers)
            '''

            del self.control_points_list[self.comboBox_2.currentText()]
            del self.bezier_curves[self.comboBox_2.currentText()]

            if self.comboBox_2.currentText() in self.line_areas:
                del self.line_areas[self.comboBox_2.currentText()]

            if not self.bezier_curves.keys():
                self.comboBox_2.addItem('No Curves')

            self.comboBox_2.removeItem(self.comboBox_2.currentIndex())

            '''
            print('\nAfter new curve')
            print(self.control_points_list)
            print(self.bezier_curves)
            print(self.line_areas)
            '''

            self.redrawCanvas()


    def selectedCurveChanged(self):

        if self.comboBox_2.currentText() == 'No Curves':
            return
        else:
            selected_curve_control_points = self.control_points_list[self.comboBox_2.currentText()]

            self.lineEdit_1.setText(str(selected_curve_control_points[0][0]))
            self.lineEdit_5.setText(str(selected_curve_control_points[0][1]))
            self.lineEdit_2.setText(str(selected_curve_control_points[1][0]))
            self.lineEdit_6.setText(str(selected_curve_control_points[1][1]))
            self.lineEdit_3.setText(str(selected_curve_control_points[2][0]))
            self.lineEdit_7.setText(str(selected_curve_control_points[2][1]))
            self.lineEdit_4.setText(str(selected_curve_control_points[3][0]))
            self.lineEdit_8.setText(str(selected_curve_control_points[3][1]))

            self.redrawCanvas()        


    def controlPoint1Clicked(self):
        
        self.control_point_1_click_count_parity = self.control_point_1_click_count_parity + 1

        if self.control_point_1_click_count_parity % 2 == 0:            
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)
            self.control_point_1_click_cursor_enable = False
            self.control_point_1_click_count_parity == 0
        else:
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.control_point_1_click_cursor_enable = True
    
    def controlPoint2Clicked(self):

        self.control_point_2_click_count_parity = self.control_point_2_click_count_parity + 1

        if self.control_point_2_click_count_parity % 2 == 0:
            self.pushButton_3.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)
            self.control_point_2_click_cursor_enable = False
            self.control_point_2_click_count_parity == 0
        else:
            self.pushButton_3.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.control_point_2_click_cursor_enable = True

    def controlPoint3Clicked(self):

        self.control_point_3_click_count_parity = self.control_point_3_click_count_parity + 1

        if self.control_point_3_click_count_parity % 2 == 0:
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_6.setEnabled(True)        
            self.control_point_3_click_cursor_enable = False
            self.control_point_3_click_count_parity == 0
        else:
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.control_point_3_click_cursor_enable = True
    
    def controlPoint4Clicked(self):

        self.control_point_4_click_count_parity = self.control_point_4_click_count_parity + 1

        if self.control_point_4_click_count_parity % 2 == 0:
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)        
            self.control_point_4_click_cursor_enable = False
            self.control_point_4_click_count_parity == 0
        else:
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
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
                self.lineEdit_1.setText(str(round(event.xdata, 2)))
                self.lineEdit_5.setText(str(round(event.ydata, 2)))

            elif self.control_point_2_click_cursor_enable:
                self.lineEdit_2.setText(str(round(event.xdata, 2)))
                self.lineEdit_6.setText(str(round(event.ydata, 2)))

            elif self.control_point_3_click_cursor_enable:
                self.lineEdit_3.setText(str(round(event.xdata, 2)))
                self.lineEdit_7.setText(str(round(event.ydata, 2)))
            
            elif self.control_point_4_click_cursor_enable:
                self.lineEdit_4.setText(str(round(event.xdata, 2)))
                self.lineEdit_8.setText(str(round(event.ydata, 2)))

    ###########################################################

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
