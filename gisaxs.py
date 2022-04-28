from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import numpy as np
import cbf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Rectangle
from scipy.signal import find_peaks
import scanning_tools as scan
import plottingtools

def loadEmpty(self):
    gisaxsmap_canvas = plottingtools.PlotWidget(xlabel="In-plane scattering angle 2$\phi{_f}$ (°)", ylabel="Out-of-plane scattering angle $\\alpha{_f}$ (°)",
                        title = "GISAXS data")

    horizontalscan_canvas = plottingtools.PlotWidget(xlabel="In-plane scattering angle 2$\phi{_f}$ (°)", ylabel="Intensity (arb. u)",
                        title = "Horizontal scan")
    verticalscan_canvas = plottingtools.PlotWidget(xlabel="Out-of-plane scattering angle $\\alpha{_f}$ (°)", ylabel="Intensity (arb. u)",
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
    self.rect = None
    self.holdVertical.setChecked(False)
    self.holdHorizontal.setChecked(False)
    self.rect = Rectangle((0, 0), 1, 1, alpha=1, fill=None, color="red")
    self.figurecanvas = None


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
        scan.scanX(self)
        scan.YonedaScan(self)
        self.firstRun = False



def detectPeak(self, data, scan="horizontal", prominence = 2):
    if scan == "horizontal":
        peakindex = find_peaks(np.log(data), prominence=prominence)[0]
    return peakindex

def getPath(self, documenttype="GISAXS data file (*.cbf);;All Files (*)"):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    path = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",documenttype, options=options)[0]
    return path

