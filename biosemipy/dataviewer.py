import os
import sys
from collections import deque
from functools import partial

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAbstractItemView, QAction, QFileDialog, \
    QInputDialog, QMainWindow, QMessageBox
from matplotlib import cm

from biosemipy.bdf import BDF
from biosemipy.gui.channel_difference import ChannelDifference
from biosemipy.gui.channel_selection import ChannelSelection
from biosemipy.gui.plot import Ui_MainWindow
from biosemipy.gui.display_text import DisplayText
from biosemipy.gui.events_table import EventsTable
from biosemipy.gui.crop import Crop
from biosemipy.gui.decimate import Decimate


pg.setConfigOptions(background="k", foreground="w", useOpenGL=True)


class DataViewer(QMainWindow):

    def __init__(self, fname=None, channels=None):

        super(DataViewer, self).__init__()

        self.fname = fname

        # visuals
        self.setWindowTitle("Data Viewer")
        self.setGeometry(0, 0, 1920, 1080)
        self.line_width = 1
        self.theme = deque(["k", "w"])
        self.colourmap = "rainbow"
        self.colours = cm.get_cmap(self.colourmap)
        self.font = QtGui.QFont("Monospace", 8)

        # signals/timers
        self.proxy = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.qt_connections = False

        # cursor for selected channel
        self.channel_selected = None
        self.cursor_on = False
        self.cursor_x_line = pg.InfiniteLine(angle=90, movable=False)
        self.cursor_y_line = pg.InfiniteLine(angle=0, movable=False)
        self.cursor_label = pg.TextItem(anchor=(0.5, 1))

        # x-region
        self.x_region = pg.LinearRegionItem()
        self.x_region_on = False
        self.plot_events = False

        # required data fields
        self.bdf = None
        self.data = None
        self.time = None
        self.n_channels = None
        self.labels_org = None
        self.labels_selected = None
        self.events = None
        self.channels = channels
        self.channel_items = []
        self.label_items = []
        self.channel_selection = []
        self.event_items = []
        self.n_events_visable = 0

        # main gui
        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)
        self.gui.plot = pg.PlotWidget(enableMenu=False, autoRange=False)
        self.gui.plot.setMouseEnabled(x=False, y=False)
        self.gui.layout.insertWidget(0, self.gui.plot)
        self.scale = self.set_scale()

        if self.fname:
            self.read_bdf_file()
            self.set_menubar(file_loaded=True)
            self.set_qt_connections(connect=True)
            self.set_plot()
            self.update_plot()
        else:
            self.set_menubar(file_loaded=False)
            self.set_plot_blank()

        self.setWindowTitle("Data Viewer")
        self.setGeometry(0, 0, 1920, 1080)

    def set_slider_values(self):
        """ Set appripriate min/max values for x/y-scale sliders. """

        self.gui.y_scale_slider.setMinimum(-5000)
        self.gui.y_scale_slider.setMaximum(-5)
        self.gui.y_scale_slider.setValue(-1000)
        self.gui.y_scale_slider.setSliderPosition(-1000)
        self.gui.y_scale_slider.setSingleStep(5)

        self.gui.y_spacing_factor_slider.setMinimum(0)
        self.gui.y_spacing_factor_slider.setMaximum(500)
        self.gui.y_spacing_factor_slider.setValue(10)
        self.gui.y_spacing_factor_slider.setSliderPosition(10)
        self.gui.y_spacing_factor_slider.setSingleStep(1)

        self.gui.x_scale_slider.setMinimum(0)
        self.gui.x_scale_slider.setMaximum(10000)
        self.gui.x_scale_slider.setValue(0)
        self.gui.x_scale_slider.setSliderPosition(0)
        self.gui.x_scale_slider.setSingleStep(10)

        self.gui.x_scroll_pos_slider.setMinimum(0)
        self.gui.x_scroll_pos_slider.setMaximum(len(self.time) - (self.scale["xrange"] + 1))
        self.gui.x_scroll_pos_slider.setValue(0)
        self.gui.x_scroll_pos_slider.setSliderPosition(0)
        self.gui.x_scroll_pos_slider.setSingleStep(100)

        self.gui.x_scroll_speed_slider.setMinimum(0)
        self.gui.x_scroll_speed_slider.setMaximum(100)
        self.gui.x_scroll_speed_slider.setValue(20)
        self.gui.x_scroll_pos_slider.setSliderPosition(20)
        self.gui.x_scroll_speed_slider.setSingleStep(5)

    def closeEvent(self, event):
        """ Window close button clicked. """

        close = QMessageBox.question(self, "QUIT", "Sure?",
                                     QMessageBox.Yes | QMessageBox.No)

        event.accept() if close == QMessageBox.Yes else event.ignore()

    def read_bdf_file(self):
        """ Read *.bdf file. """

        print("Reading {}".format(self.fname))
        if isinstance(self.fname, list):
            if len(self.fname) == 1:
                self.fname = self.fname[0]
                bdf = BDF(self.fname, chans=self.channels)
                self.merge_filenames()
            else:
                bdf = self.read_bdf_files()
        else:
            bdf = BDF(self.fname, chans=self.channels)

        self.bdf = bdf
        self.data = bdf.data
        self.time = bdf.time
        self.n_channels = np.shape(bdf.data)[0]
        self.labels_org = bdf.hdr["labels"][:-1]
        self.labels_selected = bdf.hdr["labels"][:-1]
        self.events = bdf.trig
        self.set_slider_values()
        self.set_selection_labels()

        self.set_menubar(file_loaded=True)
        self.set_qt_connections(connect=True)

    def read_bdf_files(self):
        """ Read multiple *.bdf files. """

        bdf = []
        for file in self.fname:
            bdf.append(BDF(file, chans=self.channels))
        self.merge_filenames()
        bdf[0].merge(self.fname, *bdf[1:])

        return bdf[0]

    def merge_filenames(self):
        """ Merge multiple *.bdf filenames. """

        def func(x): return os.path.splitext(os.path.split(x)[1])[0]
        name = map(func, self.fname)
        self.fname = "".join(list(name)) + ".bdf"

    @staticmethod
    def set_scale():
        """ Initial x/y scale values. """

        return dict({"type":  deque(["vertical", "butterfly"]),
                     "ymin": -500, "ymax": 500, "yrange": 1000,
                     "yspacing_offset": 0,
                     "yspacing_factor": 10, "yoffset": np.array([]),
                     "y_demean": True,
                     "xmin": 0, "xmax": 500, "xrange": 500,
                     "x_scroll": False, "x_scroll_speed": 10})

    def set_qt_connections(self, connect=False):
        """ Connect qt gui buttons/sliders to appropriate functions. """

        if connect:

            # y-scale
            self.gui.y_scale_type.clicked.connect(self.on_y_scale_type_clicked)
            self.gui.y_scale_dec.clicked.connect(partial(self.on_y_scale_clicked, 50))
            self.gui.y_scale_inc.clicked.connect(partial(self.on_y_scale_clicked, -50))
            self.gui.y_scale_slider.valueChanged.connect(self.on_y_scale_slider)

            # self.gui.y_spacing_factor_slider
            self.gui.y_spacing_dec.clicked.connect(partial(self.on_y_spacing_clicked, -0.1))
            self.gui.y_spacing_inc.clicked.connect(partial(self.on_y_spacing_clicked, 0.1))
            self.gui.y_spacing_factor_slider.valueChanged.connect(self.on_y_spacing_factor_slider)
            self.gui.y_spacing_offset_slider.valueChanged.connect(self.on_y_spacing_offset_slider)
            self.gui.y_demean.clicked.connect(self.on_y_demean)

            # x-scale
            self.gui.x_scale_dec.clicked.connect(partial(self.on_x_scale_clicked, -10))
            self.gui.x_scale_inc.clicked.connect(partial(self.on_x_scale_clicked, 10))
            self.gui.x_scale_slider.valueChanged.connect(self.on_x_scale_slider)
            self.gui.x_scroll.clicked.connect(self.on_x_scroll_clicked)
            self.gui.x_scroll_pos_slider.valueChanged.connect(self.on_x_scroll_pos_slider)
            self.gui.x_scroll_speed_dec.clicked.connect(partial(self.on_x_scroll_speed_clicked, -5))
            self.gui.x_scroll_speed_inc.clicked.connect(partial(self.on_x_scroll_speed_clicked, 5))
            self.gui.x_scroll_speed_slider.valueChanged.connect(self.on_x_scroll_speed_slider)

            # channel selection/ region / events / cursor / reset
            self.gui.channel_selection.itemSelectionChanged.connect(self.on_channel_selection)
            self.gui.x_region.clicked.connect(self.on_x_region_clicked)
            self.gui.toggle_events.clicked.connect(self.on_toggle_events_clicked)
            self.gui.toggle_cursor.clicked.connect(self.on_toggle_cursor_clicked)
            self.gui.reset.clicked.connect(self.on_reset_clicked)

        else:

            # y-scale
            self.gui.y_scale_type.clicked.disconnect()
            self.gui.y_scale_dec.clicked.disconnect()
            self.gui.y_scale_inc.clicked.disconnect()
            self.gui.y_scale_slider.valueChanged.disconnect()

            # self.gui.y_spacing_factor_slider
            self.gui.y_spacing_dec.clicked.disconnect()
            self.gui.y_spacing_inc.clicked.disconnect()
            self.gui.y_spacing_factor_slider.valueChanged.disconnect()
            self.gui.y_spacing_offset_slider.valueChanged.disconnect()
            self.gui.y_demean.clicked.disconnect()

            # x-scale
            self.gui.x_scale_dec.clicked.disconnect()
            self.gui.x_scale_inc.clicked.disconnect()
            self.gui.x_scale_slider.valueChanged.disconnect()
            self.gui.x_scroll.clicked.disconnect()
            self.gui.x_scroll_pos_slider.valueChanged.disconnect()
            self.gui.x_scroll_speed_dec.clicked.disconnect()
            self.gui.x_scroll_speed_inc.clicked.disconnect()
            self.gui.x_scroll_speed_slider.valueChanged.disconnect()

            # channel selection/ region / events / cursor / reset
            self.gui.channel_selection.itemSelectionChanged.disconnect()
            self.gui.x_region.clicked.disconnect()
            self.gui.toggle_events.clicked.disconnect()
            self.gui.toggle_cursor.clicked.disconnect()
            self.gui.reset.clicked.disconnect()

    def set_menubar(self, file_loaded=False):
        """
        Add menubar to main window. Additional options only added when
        file is loaded.
        """

        menu_bar = self.menuBar()
        menu_bar.clear()

        read_bdf_action = QAction('&Read BDF File', self)
        read_bdf_action.triggered.connect(self.select_bdf_file)

        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(read_bdf_action)

        if not file_loaded:
            return

        merge_file_action = QAction('&Merge BDF Files', self)
        merge_file_action.triggered.connect(self.on_merge_file_clicked)

        write_file_action = QAction('&Write BDF File', self)
        write_file_action.triggered.connect(self.on_write_file_clicked)

        crop_file_action = QAction('&Crop BDF File', self)
        crop_file_action.triggered.connect(self.on_crop_file_clicked)

        decimate_file_action = QAction('&Decimate BDF File', self)
        decimate_file_action.triggered.connect(self.on_decimate_file_clicked)

        file_info_action = QAction('&File Information', self)
        file_info_action.triggered.connect(self.on_file_info_clicked)

        clear_file_action = QAction('&Clear Plot', self)
        clear_file_action.triggered.connect(self.on_clear_file_clicked)

        events_toggle_action = QAction('&Toggle Events', self)
        events_toggle_action.triggered.connect(self.on_toggle_events_clicked)
        events_info_action = QAction('&Event Info', self)
        events_info_action.triggered.connect(self.on_events_info_clicked)

        channel_difference_action = QAction('&Channel Difference', self)
        channel_difference_action.triggered.connect(self.on_channel_difference_action)

        channel_select_action = QAction('&Channel Selection', self)
        channel_select_action.triggered.connect(self.on_channel_select_action)

        channel_delete_action = QAction('&Channel Deletion', self)
        channel_delete_action.triggered.connect(self.on_channel_delete_action)

        theme_action = QAction('&Invert Theme', self)
        theme_action.triggered.connect(self.invert_theme)

        colourmap_select_action = QAction('&Colourmap (select)', self)
        colourmap_select_action.triggered.connect(self.select_colourmap)

        font_size_action = QAction('&Font Size (select)', self)
        font_size_action.triggered.connect(self.select_font_size)

        line_size_action = QAction('&Line Width (select)', self)
        line_size_action.triggered.connect(self.select_line_width)

        file_menu.addAction(merge_file_action)
        file_menu.addAction(write_file_action)
        file_menu.addAction(crop_file_action)
        file_menu.addAction(decimate_file_action)
        file_menu.addAction(file_info_action)
        file_menu.addAction(clear_file_action)

        events_menu = menu_bar.addMenu('&Events')
        events_menu.addAction(events_toggle_action)
        events_menu.addAction(events_info_action)

        channel_menu = menu_bar.addMenu('&Channel')
        channel_menu.addAction(channel_difference_action)
        channel_menu.addAction(channel_select_action)
        channel_menu.addAction(channel_delete_action)

        visuals_menu = menu_bar.addMenu('&Visuals')
        visuals_menu.addAction(theme_action)
        visuals_menu.addAction(colourmap_select_action)
        visuals_menu.addAction(font_size_action)
        visuals_menu.addAction(line_size_action)

    def on_decimate_file_clicked(self):

        selection = Decimate([2, 4, 8], parent=self)
        selection.show()
        if selection.exec_():
            factor = selection.get_selection()

            self.bdf.decimate(factor)
            self.data = self.bdf.data
            self.time = self.bdf.time
            self.set_slider_values()
            self.set_plot()
            self.update_plot()

    def on_crop_file_clicked(self):

        selection = Crop(self.events["count"], self.bdf.hdr["n_recs"],
                         parent=self)
        selection.show()
        if selection.exec_():
            crop_type, val1, val2 = selection.get_selection()

            self.fname = self.fname[:-4] + "_cropped" + ".bdf"
            self.bdf.crop(self.fname, crop_type, [val1, val2])
            self.data = self.bdf.data
            self.time = self.bdf.time
            self.set_slider_values()
            self.set_plot()
            self.update_plot()

    def on_channel_select_action(self):
        """ Display specific channels. All channels remain in data. """

        selection = ChannelSelection(self.labels_selected, parent=self)
        selection.show()
        if selection.exec_():
            chans = selection.get_selection()

            self.bdf.select_channels(chans)

            # update channel info
            self.n_channels = len(chans)

            self.data = self.bdf.data
            self.labels_org = chans
            self.channel_selection = []
            self.labels_selected = chans
            self.set_selection_labels()
            self.set_plot()
            self.update_plot()

    def on_channel_delete_action(self):
        """ Delete specific channels. """

        selection = ChannelSelection(self.labels_selected, parent=self)
        selection.show()
        if selection.exec_():
            chans = selection.get_selection()

            self.bdf.delete_channels(chans)

            # update channel info
            self.n_channels -= len(chans)

            self.data = self.bdf.data
            self.labels_org = self.bdf.hdr["labels"][:-1]
            self.channel_selection = []
            self.labels_selected = self.bdf.hdr["labels"][:-1]
            self.set_selection_labels()
            self.set_plot()
            self.update_plot()

    def on_file_info_clicked(self):
        """ Display header summary information. """

        header_info = DisplayText("File Header", str(self.bdf), parent=self)
        header_info.show()

    def on_channel_difference_action(self):
        """ Calculate difference between (+ append) selected channels. """

        selection = ChannelDifference(self.labels_selected, parent=self)
        selection.show()
        if selection.exec_():
            chan1, chan2, label = selection.get_selection()

            self.bdf.channel_difference([chan1], [chan2], label)

            # update channel info
            self.channel_selection.append(self.n_channels)
            self.n_channels += 1

            self.data = self.bdf.data
            self.labels_org.append(label)
            self.labels_selected.append(label)

            self.set_selection_labels()
            self.set_plot()
            self.update_plot()

    def on_write_file_clicked(self):
        """ Write data to *.bdf file. """

        file = QFileDialog.getSaveFileName(self,
                                           "Save file",
                                           os.getcwd(),
                                           'BDF(*.bdf)')
        self.bdf.write(fname=file[0])

    def on_merge_file_clicked(self):
        """ Merge 2 (or more) *.bdf files. """

        # need to clear any currently loaded file
        self.on_clear_file_clicked()

        filenames = QFileDialog.getOpenFileNames(self, "Select File", "",
                                                 "BDF Files (*.bdf)")[0]
        if filenames:
            if self.fname is None:
                self.fname = filenames
            else:
                self.fname = [self.fname]
                for filename in filenames:
                    self.fname.append(filename)
            self.read_bdf_file()
            self.set_plot()
            self.update_plot()

    def on_y_demean(self):
        """ Set y-scale demean on/off. """

        self.scale["y_demean"] = not self.scale["y_demean"]
        if self.scale["y_demean"]:
            self.gui.y_demean.setText("Y Demean (off)")
        else:
            self.gui.y_demean.setText("Y Demean (on)")
        self.update_plot()

    def on_toggle_cursor_clicked(self):
        """ Toggle cursor on/off. """

        self.cursor_on = not self.cursor_on

        if self.cursor_on:
            self.proxy = pg.SignalProxy(self.gui.plot.scene().sigMouseMoved,
                                        rateLimit=60, slot=self.mouse_moved)
        else:
            self.proxy = None

        self.set_plot()
        self.update_plot()

    def mouse_moved(self, evt):
        """ Show x/y label of mouse cursor. """

        label_offset = np.ptp(self.gui.plot.getAxis("left").range) * 0.01

        if self.gui.plot.sceneBoundingRect().contains(evt[0]):
            point = self.gui.plot.plotItem.vb.mapSceneToView(evt[0])
            txt = ""
            if self.channel_selected is not None:

                x = point.x()
                y = point.y()
                try:
                    idx = self.labels_selected.index(self.channel_selected)
                except ValueError:
                    idx = None

                if idx is not None:
                    if self.scale["type"][0] == "vertical":
                        y -= self.scale["yoffset"][idx]
                    chn = self.labels_selected[idx]
                    txt = "{}: x={:.3f}, y={:.3f}".format(chn, x, y)
                    txt = '<span style="background-color:#FFFF00">' + txt + '</span>'
                else:
                    txt = "NA: x={:.3f}, y={:.3f}".format(x, y)
                    txt = '<span style="background-color:#FFFF00">' + txt + '</span>'

            self.cursor_label.setHtml(txt)
            self.cursor_label.setPos(point.x(), point.y() + label_offset)
            self.cursor_x_line.setPos(point.x())
            self.cursor_y_line.setPos(point.y())

    def on_y_spacing_factor_slider(self):
        """ Set y-scale spacing. """

        self.scale["yspacing_factor"] = self.gui.y_spacing_factor_slider.value()
        yrange = np.ptp(self.scale["yoffset"])
        self.gui.y_spacing_offset_slider.setMinimum(-yrange/2)
        self.gui.y_spacing_offset_slider.setMaximum(yrange/2)

        self.set_plot()
        self.update_plot()

    def on_y_spacing_offset_slider(self):
        """ Set y-scale offset. """

        self.scale["yspacing_offset"] = self.gui.y_spacing_offset_slider.value()
        self.gui.y_spacing_offset_slider.setValue(self.scale["yspacing_offset"])
        self.set_plot()
        self.update_plot()

    def on_y_spacing_clicked(self, val):
        """ Set y-scale spacing. """

        self.scale["yspacing_factor"] += val
        self.gui.y_spacing_factor_slider.blockSignals(True)
        self.gui.y_spacing_factor_slider.setValue(self.scale["yspacing_factor"])
        self.gui.y_spacing_factor_slider.blockSignals(False)
        self.set_plot()
        self.update_plot()

    def set_selection_labels(self):
        """ Set labels listed in label selection box. """

        self.gui.channel_selection.setSelectionMode(QAbstractItemView.MultiSelection)
        self.gui.channel_selection.clear()
        if self.labels_selected:
            for label in self.labels_selected:
                self.gui.channel_selection.addItem(label)
        else:
            self.gui.channel_selection.blockSignals(True)
            self.gui.channel_selection.clear()
            self.gui.channel_selection.blockSignals(False)

    def select_bdf_file(self):
        """ *.bdf file selection. """

        fname = QFileDialog.getOpenFileName(self, "Select File", "",
                                            "BDF Files (*.bdf)")[0]

        if fname:

            self.fname = fname  # need full path for read_bdf_file()
            self.read_bdf_file()
            self.fname = os.path.split(self.fname)[1]  # only filename
            self.channel_selection = []
            self.set_selection_labels()
            self.set_plot()
            self.update_plot()

    def on_clear_file_clicked(self):
        """ Clear current plot. """

        self.fname = None
        self.data = None
        self.time = None
        self.n_channels = None
        self.labels_org = None
        self.labels_selected = None
        self.events = None
        self.channels = None
        self.set_menubar(file_loaded=False)
        self.set_qt_connections(connect=False)
        self.set_plot_blank()

    def on_y_scale_type_clicked(self):
        """ Change y-scale type (vertical vs. butterfly). """

        self.scale["type"].rotate(1)
        self.set_plot()
        self.update_plot()

    def on_y_scale_clicked(self, val):
        """ Change y-scale. """

        if 0 >= self.scale["ymin"] >= -5000:
            self.scale["ymin"] -= val
            self.scale["ymax"] += val
        self.scale["yrange"] = self.scale["ymax"] - self.scale["ymin"]
        self.gui.y_scale_slider.blockSignals(True)
        self.gui.y_scale_slider.setValue(self.scale["ymin"])
        self.gui.y_scale_slider.blockSignals(False)
        self.update_plot()

    def set_axes(self, plot_type):
        """ Set axes. """

        self.gui.plot.setYRange(self.scale["ymin"] - self.scale["yspacing_offset"],
                                self.scale["ymax"] - self.scale["yspacing_offset"],
                                padding=0.05)
        self.gui.plot.setXRange(self.time[self.scale["xmin"]],
                                self.time[self.scale["xmax"]],
                                padding=0.05)

        if plot_type[0] == "vertical":
            self.gui.plot.hideAxis('left')
        elif plot_type[0] == "butterfly":
            self.gui.plot.showAxis('left')

    def on_y_scale_slider(self):
        """ Change y-scale. """

        self.scale["ymin"] = self.gui.y_scale_slider.value()
        self.scale["ymax"] = -self.gui.y_scale_slider.value()
        self.scale["yrange"] = self.scale["ymax"] - self.scale["ymin"]
        self.calculate_y_offset()
        self.gui.y_scale_slider.setValue(self.scale["ymin"])
        self.update_plot()

    def on_x_scale_clicked(self, val):
        """ Change x-scale. """

        self.scale["xmax"] += val
        if self.scale["xmax"] <= self.scale["xmin"]:
            self.scale["xmax"] = self.scale["xmin"] + 10
        self.scale["xrange"] = self.scale["xmax"] - self.scale["xmin"]
        self.gui.x_scale_slider.blockSignals(True)
        self.gui.x_scale_slider.setValue(self.gui.x_scale_slider.value() + val)
        self.gui.x_scale_slider.blockSignals(False)
        self.update_plot()

    def on_x_scale_slider(self):
        """ Change x-scale. """

        self.scale["xmax"] = self.scale["xmin"] + self.gui.x_scale_slider.value()
        if self.scale["xmax"] <= self.scale["xmin"]:
            self.scale["xmax"] = self.scale["xmin"] + 10
        if self.scale["xmax"] >= np.shape(self.data)[1]:
            self.scale["xmax"] = np.shape(self.data)[1] - 1
        self.scale["xrange"] = self.scale["xmax"] - self.scale["xmin"]
        self.update_plot()

    def on_x_scroll_clicked(self):
        """ Toggle on/off x-scale scroll. """

        self.scale["x_scroll"] = not self.scale["x_scroll"]
        if self.scale["x_scroll"]:
            self.gui.x_scroll.setText("X Scroll Auto (off)")
            self.timer.start(50)
        else:
            self.gui.x_scroll.setText("X Scroll Auto (on)")
            self.timer.stop()

    def on_x_scroll_pos_slider(self):
        """ Change x-scale position"""

        self.scale["xmin"] = self.gui.x_scroll_pos_slider.value()
        self.scale["xmax"] = self.gui.x_scroll_pos_slider.value() + self.scale["xrange"]
        if self.scale["xmax"] >= np.shape(self.data)[1]:
            self.scale["xmax"] = np.shape(self.data)[1] - 1
        if self.scale["xmin"] >= self.scale["xmax"]:
            self.scale["xmin"] = self.scale["xmax"] - self.scale["xrange"]
        self.scale["xrange"] = self.scale["xmax"] - self.scale["xmin"]
        self.update_plot()

    def on_x_scroll_speed_clicked(self, val):
        """ Change x-scalle scroll speed. """

        self.scale["x_scroll_speed"] += val
        self.gui.x_scroll_speed_slider.blockSignals(True)
        self.gui.x_scroll_speed_slider.setValue(self.scale["xmax"])
        self.gui.x_scroll_speed_slider.blockSignals(False)
        self.gui.x_scroll_speed_slider.setValue(self.scale["x_scroll_speed"])
        self.update_plot()

    def on_x_scroll_speed_slider(self):
        """ Change x-scalle scroll speed. """

        self.scale["x_scroll_speed"] = self.gui.x_scroll_speed_slider.value()
        self.update_plot()

    def inc_x_scale(self):
        """ Increment the x scale by scale scroll speed. """

        self.scale["xmin"] += self.scale["x_scroll_speed"]
        self.scale["xmax"] += self.scale["x_scroll_speed"]
        self.gui.x_scale_slider.blockSignals(True)
        self.gui.x_scale_slider.setValue(self.scale["xmax"])
        self.gui.x_scale_slider.blockSignals(False)

        self.x_region.setRegion([self.x_region.lines[1].value() +
                                 self.time[self.scale["x_scroll_speed"]],
                                 self.x_region.lines[0].value() +
                                 self.time[self.scale["x_scroll_speed"]]])

    def on_toggle_events_clicked(self):
        """ Toggle on/off show/hide events in main plot window. """

        self.plot_events = not self.plot_events
        if self.plot_events:
            self.gui.toggle_events.setText("Hide Events")
        else:
            self.gui.toggle_events.setText("Show Events")

        self.set_plot()
        self.update_plot()

    def on_events_info_clicked(self):
        """ Display summary (value: count) of events in *.bdf file. """

        events = EventsTable(self.events["count"], parent=self)
        events.show()

    def on_x_region_clicked(self):
        """ Toggle on/off x region selection. """

        self.x_region_on = not self.x_region_on
        if self.x_region_on:
            self.gui.x_region.setText("X Region Selection (off)")
        else:
            self.gui.x_region.setText("X Region Selection (on)")
        self.set_plot()
        self.update_plot()

    def on_reset_clicked(self):
        """ Reset plot. """

        self.scale = self.set_scale()
        self.channel_selection = []
        self.gui.channel_selection.clear()
        self.set_selection_labels()
        self.x_region = pg.LinearRegionItem()
        self.x_region_on = False
        self.gui.y_demean.setText("Y Demean (off)")
        self.gui.x_scroll.setText("X Scroll Auto (off)")
        self.gui.x_region.setText("X Region Selection (off)")
        self.set_plot()
        self.update_plot()

    def on_channel_selection(self):
        """ Select/show specific channels only. """

        self.channel_selection = []
        for selection in self.gui.channel_selection.selectedItems():
            if selection.text() in self.labels_org:
                self.channel_selection.append(self.labels_org.index(selection.text()))
        self.set_plot()
        self.update_plot()

    def set_plot_blank(self):
        """ Reset plot to empty. """

        self.gui.plot.setTitle(title=self.fname)
        self.gui.plot.clear()
        self.gui.plot.showGrid(x=True, y=True)
        self.gui.plot.hideAxis('left')
        self.gui.plot.hideAxis('bottom')
        self.gui.channel_selection.blockSignals(True)
        self.gui.channel_selection.clear()
        self.gui.channel_selection.blockSignals(False)

    def set_plot(self):
        """ Reset plot. """

        self.gui.plot.clear()
        self.gui.plot.setTitle(title=os.path.split(self.fname)[1])
        self.gui.plot.showGrid(x=True, y=True)
        self.gui.plot.setLabel('bottom', 'Time', units='S')
        self.gui.plot.getAxis("bottom").tickFont = self.font

        self.channel_items = []
        self.label_items = []
        self.labels_selected = []
        if not self.channel_selection:
            self.channel_selection = list(range(self.n_channels))
        self.calculate_y_offset()

        colour_idx = np.linspace(0, self.colours.N, self.n_channels)
        for channel in self.channel_selection:

            colour = self.colours(int(colour_idx[channel]), bytes=True)

            channel_item = pg.PlotCurveItem(pen=pg.mkPen(colour, width=self.line_width))
            channel_item.setClickable(self)
            channel_item.sigClicked.connect(self.on_channel_selected)
            self.channel_items.append(channel_item)
            self.gui.plot.addItem(channel_item)

            self.labels_selected.append(self.labels_org[channel])
            label_item = pg.TextItem(text=self.labels_org[channel],
                                     color=colour,
                                     anchor=(0, 0.5))
            label_item.setFont(self.font)
            self.label_items.append(label_item)
            self.gui.plot.addItem(label_item)

        if self.x_region_on:
            self.gui.plot.addItem(self.x_region, ignoreBounds=True)

        if self.cursor_on:
            self.gui.plot.addItem(self.cursor_x_line, ignoreBounds=True)
            self.gui.plot.addItem(self.cursor_y_line, ignoreBounds=True)
            self.gui.plot.addItem(self.cursor_label)

        self.set_axes(self.scale["type"])

    def update_plot(self):
        """ Update plot. """

        data, time = self.crop_x_dimension()

        if self.scale["y_demean"]:
            data = self.demean_data(data)

        self.set_axes(self.scale["type"])

        if self.scale["x_scroll"]:
            self.inc_x_scale()

        # channel data
        if self.scale["type"][0] == "vertical":
            for idx, channel in enumerate(self.channel_items):
                channel.setData(time, data[idx, :])
                channel.setPos(0, self.scale["yoffset"][idx])
        elif self.scale["type"][0] == "butterfly":
            for idx, channel in enumerate(self.channel_items):
                channel.setData(time, data[idx, :])

        # labels
        label_pos_y = self.gui.plot.getAxis("bottom").range[0]
        for idx, label in enumerate(self.label_items):
            label.setPos(label_pos_y, self.scale["yoffset"][idx])

        # events
        if self.plot_events:
            self._plot_events()

    def _plot_events(self):
        """ Show events as vertical line with corresponding event code. """

        idx = self.events["idx"]
        val = self.events["val"]
        xmin, xmax = self.scale["xmin"], self.scale["xmax"]

        for _ in range(self.n_events_visable):
            self.gui.plot.removeItem(self.gui.plot.plotItem.items[-1])

        visible_idx = (idx >= xmin) & (idx <= xmax)
        events = idx[visible_idx]
        values = val[visible_idx]

        self.n_events_visable = 0
        for item in zip(events, values):
            event = pg.InfiniteLine([self.time[item[0]], 0],
                                    pen=pg.mkPen("w"),
                                    label=str(item[1]))
            event.label.setFont(self.font)
            event.label.setPosition(0.95)
            event.setAngle(90)
            self.gui.plot.addItem(event, ignoreBounds=False)
            self.n_events_visable += 1

    def crop_x_dimension(self):
        """ Crop data along the x-dimnsion for plotting. """

        data = self.data[self.channel_selection,
                         self.scale["xmin"]:self.scale["xmax"]]
        time = self.time[self.scale["xmin"]:self.scale["xmax"]]

        return data, time

    def calculate_y_offset(self):
        """ Calculated a y-scale offset for the stacked vertical display. """

        if not self.channel_selection:
            n_chans = self.n_channels
        else:
            n_chans = len(self.channel_selection)
        self.scale["yoffset"] = np.linspace(self.scale["ymax"],
                                            self.scale["ymin"],
                                            n_chans)
        self.scale["yoffset"] *= (self.scale["yspacing_factor"] / 10)

    @staticmethod
    def demean_data(data):
        """ Remove data mean. """

        return data - np.mean(data, 1, keepdims=True)

    def on_channel_selected(self, channel):
        """
        Toggle linewidth and label size when line selected with left
        mouse click.
        """

        font_size = self.font.pointSize()
        line_width = self.line_width

        for idx, item in enumerate(zip(self.channel_items, self.label_items)):
            if item[0] is channel:
                if item[0].opts["pen"].width() == self.line_width:
                    item[0].opts["pen"].setWidth(line_width * 2)
                    self.font.setPointSize(font_size * 2)
                    item[1].setFont(self.font)
                    self.font.setPointSize(font_size)
                    self.channel_selected = self.labels_selected[idx]
                else:
                    item[0].opts["pen"].setWidth(self.line_width)
                    self.font.setPointSize(font_size)
                    item[1].setFont(self.font)
                    self.channel_selected = None
            else:
                item[0].opts["pen"].setWidth(self.line_width)
                self.font.setPointSize(font_size)
                item[1].setFont(self.font)

        if self.cursor_on:
            self.simulate_mouse_movment()

    @staticmethod
    def simulate_mouse_movment():
        """ Called when cursor is on to simulate mouse movement. """

        cursor = QtGui.QCursor()
        point = cursor.pos()
        x, y = point.x(), point.y()
        cursor.setPos(x+1, y+1)

    def select_colourmap(self):
        """ Select colourmap used for the plot lines. """

        item, ok = QInputDialog.getItem(self,
                                        "Select Colourmap",
                                        "Colourmaps",
                                        cm.cmap_d.keys())

        if ok and item:
            self.colourmap = item
            self.colours = cm.get_cmap(self.colourmap)
        if self.fname is not None:
            self.set_plot()
            self.update_plot()

    def invert_theme(self):
        """ Toggle background/foreground with white/black. """

        self.theme.rotate(1)
        pg.setConfigOptions(background=self.theme[0], foreground=self.theme[1])
        self.gui.layout.removeWidget(self.gui.plot)
        self.gui.plot = pg.PlotWidget(enableMenu=False)
        self.gui.layout.insertWidget(0, self.gui.plot)
        if self.fname is None:
            self.set_plot_blank()
        else:
            self.set_plot()
            self.update_plot()

    def select_font_size(self):
        """ Change the text fontsize. """

        font_sizes = [str(i) for i in range(6, 24)]
        font_size, ok = QInputDialog.getItem(self,
                                             "Select Colourmap",
                                             "Font Size",
                                             font_sizes)

        if ok and font_size:
            self.font.setPointSize(int(font_size))
        if self.fname is not None:
            self.set_plot()
            self.update_plot()

    def select_line_width(self):
        """ Change the linewidth of the plot lines. """

        line_widths = [str(i) for i in range(1, 11)]
        line_width, ok = QInputDialog.getItem(self,
                                              "Line Width",
                                              "Line Width",
                                              line_widths)

        if ok and line_width:
            self.line_width = float(line_width)
        if self.fname is not None:
            self.set_plot()
            self.update_plot()


def run(fname=None):

    app = QtGui.QApplication(sys.argv)
    if fname is not None:
        ex = DataViewer(fname)
    else:
        ex = DataViewer()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
