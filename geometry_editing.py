from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backend_bases import MouseButton

import matplotlib
import matplotlib.pyplot as plt

def left_mouse_clicked(event):
    if event.button is MouseButton.LEFT:
        print('\nMouse Clicked!')
        print('\nMouse X Data: ', event.xdata)
        print('Mouse Y Data: ', event.ydata)
        print('\nMouse X Coordinate: ', event.x)
        print('Mouse Y Coordinate: ', event.y)

matplotlib.use('Qt5Agg')

window_width = 1280
window_height = 720
boundary_size = 100
boundaries_x = [0, 0, window_width, window_width, 0]
boundaries_y = [window_height, 0, 0, window_height, window_height]

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
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

        figure, self.axes = plt.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        control_points_1 = [(float(0 * window_width), float(0 * window_height)), (float(0.5 * window_width), float(0.5 * window_height)), (float(0 * window_width), float(1 * window_height)), (float(0 * window_width), float(1 * window_height))]
        control_points_2 = [(float(0 * window_width), float(1 * window_height)), (float(0.5 * window_width), float(0 * window_height)), (float(1 * window_width), float(1 * window_height)), (float(1 * window_width), float(1 * window_height))]
        control_points_3 = [(float(1 * window_width), float(0 * window_height)), (float(0.5 * window_width), float(0.5 * window_height)), (float(1 * window_width), float(1 * window_height)), (float(1 * window_width), float(1 * window_height))]
        
        initial_sets_of_control_points = [control_points_1, control_points_2, control_points_3]

        self.control_points_list = {}
        self.bezier_curves = {}

        self.index = 0

        #'''
        for control_points in initial_sets_of_control_points:
            self.index = self.index + 1
            self.control_points_list['Curve ' + str(self.index)] = control_points
            self.bezier_curves['Curve ' + str(self.index)] = PathPatch(Path(control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none')
            
        for curve in self.bezier_curves:
            self.axes.add_patch(self.bezier_curves[curve])
        #'''

        plt.connect('button_press_event', left_mouse_clicked)

        self.horizontalLayout_1.addWidget(self.canvas)

        #####################################################################

        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(850, 90, 401, 481))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 231))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_1.setObjectName("verticalLayout_1")
        self.comboBox_1 = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox_1.setObjectName("comboBox_1")
        self.verticalLayout_1.addWidget(self.comboBox_1)

        #####################################################################
        
        client_servers_info_file = open('projectors.txt', 'r')

        self.client_servers_IP_addresses = []

        for line in client_servers_info_file:
            self.client_servers_IP_addresses.append(line.removesuffix('\n'))

        #print(projectors)
        client_servers_info_file.close()

        self.projector_numbers = []
        self.projector_count = 0

        for projector in self.client_servers_IP_addresses:
            self.projector_count = self.projector_count + 1 
            self.projector_numbers.append('Projector ' + str(self.projector_count) + ' (' + projector + ')')

        self.comboBox_1.addItems(self.projector_numbers)

        #####################################################################

        self.gridLayout_1 = QtWidgets.QGridLayout()
        self.gridLayout_1.setObjectName("gridLayout_1")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lineEdit_1 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.gridLayout_3.addWidget(self.lineEdit_1, 0, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_3.addWidget(self.pushButton_2, 4, 3, 1, 1)
        self.pushButton_1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_1.setObjectName("pushButton_1")

        #####################################################################
    
        self.pushButton_1.clicked.connect(self.add_new_curve_clicked)
        self.pushButton_2.clicked.connect(self.remove_curve_clicked)

        #####################################################################

        self.gridLayout_3.addWidget(self.pushButton_1, 4, 1, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_3.addWidget(self.lineEdit_3, 2, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_3.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout_3.addWidget(self.lineEdit_4, 3, 1, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout_3.addWidget(self.lineEdit_5, 0, 3, 1, 1)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridLayout_3.addWidget(self.lineEdit_6, 1, 3, 1, 1)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout_3.addWidget(self.lineEdit_7, 2, 3, 1, 1)
        self.lineEdit_8 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.gridLayout_3.addWidget(self.lineEdit_8, 3, 3, 1, 1)
        self.gridLayout_1.addLayout(self.gridLayout_3, 1, 2, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox_2.setObjectName("comboBox_2")

        #####################################################################

        '''
        print(self.bezier_curves.keys())
        self.bezier_curves.clear()
        print(self.bezier_curves.keys())
        '''
        
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

            self.redraw_canvas(remove_curve = False)
        
        self.comboBox_2.currentTextChanged.connect(self.selected_curve_changed)

        #####################################################################

        self.gridLayout_1.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_1.setObjectName("label_1")
        self.gridLayout_2.addWidget(self.label_1, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_5.setObjectName("pushButton_5")

        ####################################################################

        self.pushButton_5.clicked.connect(self.set_control_points)

        ####################################################################

        self.gridLayout_2.addWidget(self.pushButton_5, 4, 0, 1, 1)
        self.gridLayout_1.addLayout(self.gridLayout_2, 1, 1, 1, 1)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_10 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_10.setObjectName("label_10")
        self.gridLayout_8.addWidget(self.label_10, 0, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_9.setObjectName("label_9")
        self.gridLayout_8.addWidget(self.label_9, 0, 1, 1, 1)
        self.gridLayout_1.addLayout(self.gridLayout_8, 0, 2, 1, 1)
        self.verticalLayout_1.addLayout(self.gridLayout_1)
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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Geometry Editing - Edge Blending"))
        self.pushButton_2.setText(_translate("MainWindow", "Remove curve"))
        self.pushButton_1.setText(_translate("MainWindow", "Add new curve"))
        self.label_1.setText(_translate("MainWindow", "Control Point 1"))
        self.label_3.setText(_translate("MainWindow", "Control Point 3"))
        self.label_2.setText(_translate("MainWindow", "Control Point 2"))
        self.label_4.setText(_translate("MainWindow", "Control Point 4"))
        self.pushButton_5.setText(_translate("MainWindow", "Set Control Points"))
        self.label_10.setText(_translate("MainWindow", "X"))
        self.label_9.setText(_translate("MainWindow", "Y"))

    ###########################################################
    
    def redraw_canvas(self, remove_curve):
        self.axes.clear()

        #if remove_curve == False:
        
        if self.comboBox_2.currentText() != 'No Curves':
            for control_points in self.control_points_list[self.comboBox_2.currentText()]:
                self.axes.plot(control_points[0], control_points[1], 'ko')

        for curve in self.bezier_curves:
            if curve == self.comboBox_2.currentText():
                self.bezier_curves[curve].set(edgecolor = 'r')
            else:
                self.bezier_curves[curve].set(edgecolor = 'k')
            self.axes.add_patch(self.bezier_curves[curve])


        self.axes.set_xlim((0 - boundary_size, window_width + boundary_size))
        self.axes.set_ylim((0 - boundary_size, window_height + boundary_size))
        self.axes.grid(color = 'k')
        self.axes.plot(boundaries_x, boundaries_y, linestyle = '--', color = 'b')
        self.canvas.draw() 

    def set_control_points(self):      
        if self.comboBox_2.currentText() == 'No Curves':
            return
        else:
            user_control_point_1_x = float(self.lineEdit_1.text())
            user_control_point_2_x = float(self.lineEdit_2.text())
            user_control_point_3_x = float(self.lineEdit_3.text())
            user_control_point_4_x = float(self.lineEdit_4.text())
            user_control_point_1_y = float(self.lineEdit_5.text())
            user_control_point_2_y = float(self.lineEdit_6.text())
            user_control_point_3_y = float(self.lineEdit_7.text())
            user_control_point_4_y = float(self.lineEdit_8.text())

            new_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]
            self.control_points_list[self.comboBox_2.currentText()] = new_control_points
            self.bezier_curves[self.comboBox_2.currentText()] = PathPatch(Path(new_control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none')

            self.redraw_canvas(remove_curve = False)
        
    def add_new_curve_clicked(self):

        '''
        print('\nBefore new curve')
        print(self.control_points_list)
        '''
        
        user_control_point_1_x = float(self.lineEdit_1.text())
        user_control_point_2_x = float(self.lineEdit_2.text())
        user_control_point_3_x = float(self.lineEdit_3.text())
        user_control_point_4_x = float(self.lineEdit_4.text())
        user_control_point_1_y = float(self.lineEdit_5.text())
        user_control_point_2_y = float(self.lineEdit_6.text())
        user_control_point_3_y = float(self.lineEdit_7.text())
        user_control_point_4_y = float(self.lineEdit_8.text())

        new_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]

        new_bezier_curve = PathPatch(Path(new_control_points, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc = 'none')
        self.index = self.index + 1
        self.control_points_list['Curve ' + str(self.index)] = new_control_points
        self.bezier_curves['Curve ' + str(self.index)] = new_bezier_curve

        self.comboBox_2.addItem('Curve ' + str(self.index))
        self.axes.add_patch(new_bezier_curve)
        self.canvas.draw()

        if self.comboBox_2.currentText() == 'No Curves':
            self.comboBox_2.removeItem(self.comboBox_2.currentIndex())
        else:
            self.comboBox_2.setCurrentText('Curve ' + str(self.index))

        '''
        print('\nAfter new curve')
        print(self.control_points_list)
        '''

    def remove_curve_clicked(self):

        if self.comboBox_2.currentText() == 'No Curves':
            return
        else:
            '''            
            print('\nBefore new curve')
            print(self.control_points_list)
            print(self.bezier_curves)
            '''  

            '''
            user_control_point_1_x = float(self.lineEdit_1.text())
            user_control_point_2_x = float(self.lineEdit_2.text())
            user_control_point_3_x = float(self.lineEdit_3.text())
            user_control_point_4_x = float(self.lineEdit_4.text())
            user_control_point_1_y = float(self.lineEdit_5.text())
            user_control_point_2_y = float(self.lineEdit_6.text())
            user_control_point_3_y = float(self.lineEdit_7.text())
            user_control_point_4_y = float(self.lineEdit_8.text())

            remove_control_points = [(user_control_point_1_x, user_control_point_1_y), (user_control_point_2_x, user_control_point_2_y), (user_control_point_3_x, user_control_point_3_y), (user_control_point_4_x, user_control_point_4_y)]
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

            if not self.bezier_curves.keys():
                self.comboBox_2.addItem('No Curves')
            
            self.comboBox_2.removeItem(self.comboBox_2.currentIndex())

            '''
            print('\nAfter new curve')
            print(self.control_points_list)
            print(self.bezier_curves)
            '''

            self.redraw_canvas(remove_curve = True)


    def selected_curve_changed(self):

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

            self.redraw_canvas(remove_curve = False)        

    ###########################################################


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
