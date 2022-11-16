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
    """Create a layout to plat a graph on."""

    toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(canvas)
    layout.addWidget(toolbar)
    
def loadMap_from_file_picker(self):
    """Load the GISAXS map after selecting it from the file picker."""
    path = getPath(self)
    loadMap(self, path)

def set_ROI_mode(self, mode = "ROI"):
    """Set ROI to either regular ROI or Background mode."""
    if mode == "ROI":
        setter1 = True
        setter2 = False
    elif mode == "background":
        setter1 = False
        setter2 = True

    self.ROI_button.setChecked(setter1)
    self.bg_ROI_button.setChecked(setter2)
    self.ROI_scan_rect.set_visible(setter1)
    self.ROI_scan_rect.set_active(setter1)
    self.ROI_background_rect.set_visible(setter2)
    self.ROI_background_rect.set_active(setter2)


def loadMap(self, file):
    """Load the the selected GISAXS map."""

    if self.ROI_scan_rect == None:
        self.connectActions()
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
        try:
            self.define_rectangle()
            set_ROI_mode(self, "ROI")
            scan.find_specular(self)
            scan.detector_scan(self)
            self.holdHorizontal.setChecked(False)
            scan.YonedaScan(self)
        except:
            print("Error doing preset runs")
        self.firstRun = False


def getPath(self, documenttype="GISAXS data file (*.cbf);;All Files (*)"):
    """Get the path from the file picker."""
    options = QFileDialog.Options()
    path = QFileDialog.getOpenFileName(self,"Open GISAXS data file", "",documenttype, options=options)[0]
    return path

