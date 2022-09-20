from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
import os
import numpy as np
import cbf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import scanning_tools as scan
from sample import Sample
import plottingtools
import settings

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
    create_layout(self, horizontalscan_canvas, self.horizontal_layout)
    create_layout(self, verticalscan_canvas, self.vertical_layout)

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
        self.figurecanvas = plottingtools.singlePlotonCanvas(self, layout, data, title = filename, style = "default")
        self.fwhmscan_button.clicked.connect(lambda: fwhmscan.open_fwhmscan_window(self))
        try:
            self.define_rectangle()
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

