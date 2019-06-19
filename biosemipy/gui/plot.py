# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plot.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1057, 1172)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setObjectName("layout")
        self.y_spacing_offset_slider = QtWidgets.QScrollBar(self.centralwidget)
        self.y_spacing_offset_slider.setOrientation(QtCore.Qt.Vertical)
        self.y_spacing_offset_slider.setObjectName("y_spacing_offset_slider")
        self.layout.addWidget(self.y_spacing_offset_slider)
        self.control_grid = QtWidgets.QGridLayout()
        self.control_grid.setObjectName("control_grid")
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.control_grid.addItem(spacerItem, 22, 0, 1, 1)
        self.x_scroll = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_scroll.sizePolicy().hasHeightForWidth())
        self.x_scroll.setSizePolicy(sizePolicy)
        self.x_scroll.setObjectName("x_scroll")
        self.control_grid.addWidget(self.x_scroll, 11, 0, 1, 2)
        self.x_scroll_speed_inc = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_scroll_speed_inc.sizePolicy().hasHeightForWidth()
        )
        self.x_scroll_speed_inc.setSizePolicy(sizePolicy)
        self.x_scroll_speed_inc.setObjectName("x_scroll_speed_inc")
        self.control_grid.addWidget(self.x_scroll_speed_inc, 13, 1, 1, 1)
        self.reset = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset.sizePolicy().hasHeightForWidth())
        self.reset.setSizePolicy(sizePolicy)
        self.reset.setObjectName("reset")
        self.control_grid.addWidget(self.reset, 20, 0, 1, 2)
        self.x_scroll_speed_dec = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_scroll_speed_dec.sizePolicy().hasHeightForWidth()
        )
        self.x_scroll_speed_dec.setSizePolicy(sizePolicy)
        self.x_scroll_speed_dec.setObjectName("x_scroll_speed_dec")
        self.control_grid.addWidget(self.x_scroll_speed_dec, 13, 0, 1, 1)
        self.x_region = QtWidgets.QPushButton(self.centralwidget)
        self.x_region.setObjectName("x_region")
        self.control_grid.addWidget(self.x_region, 17, 0, 1, 2)
        self.control_grid_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.control_grid_label.sizePolicy().hasHeightForWidth()
        )
        self.control_grid_label.setSizePolicy(sizePolicy)
        self.control_grid_label.setAlignment(QtCore.Qt.AlignCenter)
        self.control_grid_label.setObjectName("control_grid_label")
        self.control_grid.addWidget(self.control_grid_label, 0, 0, 1, 2)
        self.y_scale_inc = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_scale_inc.sizePolicy().hasHeightForWidth())
        self.y_scale_inc.setSizePolicy(sizePolicy)
        self.y_scale_inc.setObjectName("y_scale_inc")
        self.control_grid.addWidget(self.y_scale_inc, 2, 1, 1, 1)
        self.y_spacing_inc = QtWidgets.QPushButton(self.centralwidget)
        self.y_spacing_inc.setObjectName("y_spacing_inc")
        self.control_grid.addWidget(self.y_spacing_inc, 4, 1, 1, 1)
        self.x_scale_inc = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_scale_inc.sizePolicy().hasHeightForWidth())
        self.x_scale_inc.setSizePolicy(sizePolicy)
        self.x_scale_inc.setObjectName("x_scale_inc")
        self.control_grid.addWidget(self.x_scale_inc, 8, 1, 1, 1)
        self.y_scale_type = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_scale_type.sizePolicy().hasHeightForWidth())
        self.y_scale_type.setSizePolicy(sizePolicy)
        self.y_scale_type.setObjectName("y_scale_type")
        self.control_grid.addWidget(self.y_scale_type, 1, 0, 1, 2)
        self.y_spacing_factor_slider = QtWidgets.QScrollBar(self.centralwidget)
        self.y_spacing_factor_slider.setOrientation(QtCore.Qt.Horizontal)
        self.y_spacing_factor_slider.setObjectName("y_spacing_factor_slider")
        self.control_grid.addWidget(self.y_spacing_factor_slider, 6, 0, 1, 2)
        self.x_scroll_pos_slider = QtWidgets.QScrollBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_scroll_pos_slider.sizePolicy().hasHeightForWidth()
        )
        self.x_scroll_pos_slider.setSizePolicy(sizePolicy)
        self.x_scroll_pos_slider.setOrientation(QtCore.Qt.Horizontal)
        self.x_scroll_pos_slider.setObjectName("x_scroll_pos_slider")
        self.control_grid.addWidget(self.x_scroll_pos_slider, 12, 0, 1, 2)
        self.x_scale_slider = QtWidgets.QScrollBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_scale_slider.sizePolicy().hasHeightForWidth()
        )
        self.x_scale_slider.setSizePolicy(sizePolicy)
        self.x_scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.x_scale_slider.setObjectName("x_scale_slider")
        self.control_grid.addWidget(self.x_scale_slider, 9, 0, 1, 2)
        self.y_spacing_dec = QtWidgets.QPushButton(self.centralwidget)
        self.y_spacing_dec.setObjectName("y_spacing_dec")
        self.control_grid.addWidget(self.y_spacing_dec, 4, 0, 1, 1)
        self.toggle_events = QtWidgets.QPushButton(self.centralwidget)
        self.toggle_events.setObjectName("toggle_events")
        self.control_grid.addWidget(self.toggle_events, 18, 0, 1, 2)
        self.y_scale_slider = QtWidgets.QScrollBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.y_scale_slider.sizePolicy().hasHeightForWidth()
        )
        self.y_scale_slider.setSizePolicy(sizePolicy)
        self.y_scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.y_scale_slider.setObjectName("y_scale_slider")
        self.control_grid.addWidget(self.y_scale_slider, 3, 0, 1, 2)
        self.x_scale_dec = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_scale_dec.sizePolicy().hasHeightForWidth())
        self.x_scale_dec.setSizePolicy(sizePolicy)
        self.x_scale_dec.setObjectName("x_scale_dec")
        self.control_grid.addWidget(self.x_scale_dec, 8, 0, 1, 1)
        self.x_scroll_speed_slider = QtWidgets.QScrollBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_scroll_speed_slider.sizePolicy().hasHeightForWidth()
        )
        self.x_scroll_speed_slider.setSizePolicy(sizePolicy)
        self.x_scroll_speed_slider.setOrientation(QtCore.Qt.Horizontal)
        self.x_scroll_speed_slider.setObjectName("x_scroll_speed_slider")
        self.control_grid.addWidget(self.x_scroll_speed_slider, 16, 0, 1, 2)
        self.y_scale_dec = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_scale_dec.sizePolicy().hasHeightForWidth())
        self.y_scale_dec.setSizePolicy(sizePolicy)
        self.y_scale_dec.setObjectName("y_scale_dec")
        self.control_grid.addWidget(self.y_scale_dec, 2, 0, 1, 1)
        self.toggle_cursor = QtWidgets.QPushButton(self.centralwidget)
        self.toggle_cursor.setObjectName("toggle_cursor")
        self.control_grid.addWidget(self.toggle_cursor, 19, 0, 1, 2)
        self.y_demean = QtWidgets.QPushButton(self.centralwidget)
        self.y_demean.setObjectName("y_demean")
        self.control_grid.addWidget(self.y_demean, 7, 0, 1, 2)
        self.layout.addLayout(self.control_grid)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(160, 16777215))
        self.label.setSizeIncrement(QtCore.QSize(0, 0))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.channel_selection = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.channel_selection.sizePolicy().hasHeightForWidth()
        )
        self.channel_selection.setSizePolicy(sizePolicy)
        self.channel_selection.setMaximumSize(QtCore.QSize(160, 16777215))
        self.channel_selection.setSizeIncrement(QtCore.QSize(0, 0))
        self.channel_selection.setObjectName("channel_selection")
        self.verticalLayout_2.addWidget(self.channel_selection)
        self.layout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.layout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionColourmap = QtWidgets.QAction(MainWindow)
        self.actionColourmap.setObjectName("actionColourmap")
        self.actionLight = QtWidgets.QAction(MainWindow)
        self.actionLight.setObjectName("actionLight")
        self.actionDark = QtWidgets.QAction(MainWindow)
        self.actionDark.setObjectName("actionDark")

        self.retranslateUi(MainWindow)
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.x_scroll.setText(_translate("MainWindow", "X Scroll Auto (on)"))
        self.x_scroll_speed_inc.setText(_translate("MainWindow", "Speed (+)"))
        self.reset.setText(_translate("MainWindow", "Reset"))
        self.x_scroll_speed_dec.setText(_translate("MainWindow", "Speed (-)"))
        self.x_region.setText(_translate("MainWindow", "X Region Selection (on)"))
        self.control_grid_label.setText(_translate("MainWindow", "X/Y Scale"))
        self.y_scale_inc.setText(_translate("MainWindow", "Y Scale (+)"))
        self.y_spacing_inc.setText(_translate("MainWindow", "Y Spacing (+)"))
        self.x_scale_inc.setText(_translate("MainWindow", "X (+)"))
        self.y_scale_type.setText(_translate("MainWindow", "Scale Type"))
        self.y_spacing_dec.setText(_translate("MainWindow", "Y Spacing (-)"))
        self.toggle_events.setText(_translate("MainWindow", "Show Events"))
        self.x_scale_dec.setText(_translate("MainWindow", "X (-)"))
        self.y_scale_dec.setText(_translate("MainWindow", "Y Scale (-)"))
        self.toggle_cursor.setText(_translate("MainWindow", "Cursor"))
        self.y_demean.setText(_translate("MainWindow", "Y Demean (off)"))
        self.label.setText(_translate("MainWindow", "Channels"))
        self.actionColourmap.setText(_translate("MainWindow", "&Colourmap"))
        self.actionLight.setText(_translate("MainWindow", "&Light"))
        self.actionDark.setText(_translate("MainWindow", "&Dark"))
