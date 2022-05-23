from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import numpy as np
import cbf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.signal import find_peaks
import scanning_tools as scan
from sample import Sample
import plottingtools
import settings
from roi import ROI

def get_labels():
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
        self.figurecanvas[1].canvas.mpl_connect('button_press_event', self.on_press)
        self.figurecanvas[1].canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.figurecanvas[1].canvas.mpl_connect('button_release_event', self.on_release)
        self.figurecanvas[0].ax = plt.gca()
        try:
            scan.find_specular(self)
            scan.detector_scan(self)
            self.holdHorizontal.setChecked(False)
            scan.YonedaScan(self)
        except:
            print("Error doing preset runs")
        self.firstRun = False



def detectPeak(self, data, scan="horizontal", prominence = 2):
    if scan == "horizontal":
        peakindex = find_peaks(np.log(data), prominence=prominence)[0]
    return peakindex

def getPath(self, documenttype="GISAXS data file (*.cbf);;All Files (*)"):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    path = QFileDialog.getOpenFileName(self,"Open GISAXS data file", "",documenttype, options=options)[0]
    return path

