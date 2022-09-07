from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import numpy as np
import cbf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector
import scanning_tools as scan
from sample import Sample
import plottingtools
import settings
from roi import ROI

def get_labels():
    """Retreive label names for current mapping"""

    mapping = settings.get_config("mapping")
    if mapping == "Angular":
        in_plane_label = "In-plane scattering angle $\phi{_f}$ (°)"
        out_of_plane_label = "Out-of-plane scattering angle $\\alpha{_f}$ (°)"
    if mapping == "q-space":
        in_plane_label = "In-plane scattering vector q${_y}$ (Å$^{-1}$)"
        out_of_plane_label = "Out-of-plane scattering vector q${_z}$ (Å$^{-1}$)"
    if mapping == "Pixels":
        in_plane_label = "Horizontal detector position (pixels)"
        out_of_plane_label = "Vertical detector position (pixels)"
    return in_plane_label, out_of_plane_label

def loadEmpty(self):
    """Load empty graphs without any data for initial setup."""

    in_plane_label, out_of_plane_label = get_labels()
    gisaxsmap_canvas = plottingtools.PlotWidget(xlabel=in_plane_label, ylabel=out_of_plane_label,
                        title = "GISAXS data")

    horizontalscan_canvas = plottingtools.PlotWidget(xlabel=in_plane_label, ylabel="Intensity (arb. u)",
                        title = "Horizontal scan")
    verticalscan_canvas = plottingtools.PlotWidget(xlabel=out_of_plane_label, ylabel="Intensity (arb. u)",
                        title = "Vertical scan")
    create_layout(self, gisaxsmap_canvas, self.maplayout)
    create_layout(self, horizontalscan_canvas, self.graphlayout)
    create_layout(self, verticalscan_canvas, self.graphlayout)

def create_layout(self, canvas, layout):
    toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(canvas)
    layout.addWidget(toolbar)

def loadMap_from_file_picker(self):
    path = getPath(self)
    loadMap(self, path)

def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

def passy(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))

def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(x1)
    print(x2)
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))


def loadMap(self, file):
    self.firstRun = True
    self.holdVertical.setChecked(False)
    self.holdHorizontal.setChecked(False)
    self.figurecanvas = None
    self.ROI_scan = ROI((0, 0), 0, 0, alpha=1, fill=None, color="red")
    self.ROI_background = ROI((0, 0), 0, 0, alpha=1, fill=None, color="yellow")
    self.ROI_background.set_visible(False)
    self.sampledata = Sample()

    if file != "":
        path = os.path.dirname(file)
        filename = Path(file).name
        os.chdir(path)
        self.filename = filename
        contents = cbf.read(filename)
        data = contents.data
        self.sampledata.gisaxs_data = data
        self.sampledata.path = file
        layout = self.maplayout
        self.clearLayout(self.maplayout)
        self.figurecanvas = plottingtools.singlePlotonCanvas(self, layout, data, title = filename)

        # self.ROI_scan_rect = RectangleSelector(self.figurecanvas[0].axes[0], line_select_callback,
        #                                        drawtype='box', useblit=False,
        #                                        button=[1],  # don't use middle button
        #                                        minspanx=0.1, minspany=0.1,
        #                                        spancoords='pixels',
        #                                        interactive=True)
        self.figurecanvas[1].canvas.mpl_connect('button_press_event', self.on_press)
        self.figurecanvas[1].canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.figurecanvas[1].canvas.mpl_connect('button_release_event', self.on_release)

        gisaxs_figure = self.figurecanvas[0]
        ax = gisaxs_figure.axes[0]
        ax.add_patch(self.ROI_scan)
        ax.add_patch(self.ROI_background)
        self.background = gisaxs_figure.canvas.copy_from_bbox(ax.bbox)
        self.figurecanvas[0].ax = plt.gca()
        try:
            scan.find_specular(self)
            scan.detector_scan(self)
            self.holdHorizontal.setChecked(False)
            scan.YonedaScan(self)
        except:
            print("Error doing preset runs")
        self.firstRun = False

def getPath(self, documenttype="GISAXS data file (*.cbf);;All Files (*)"):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    path = QFileDialog.getOpenFileName(self,"Open GISAXS data file", "",documenttype, options=options)[0]
    return path

