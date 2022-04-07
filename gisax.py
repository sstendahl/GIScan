from PyQt5.QtWidgets import QFileDialog, QShortcut
from pathlib import Path
import os
import numpy as np
import cbf
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from scipy.signal import find_peaks

def detectPeak(self, data, scan="horizontal", prominence = 2):
    if scan == "horizontal":
        peakindex = find_peaks(np.log(data), prominence=prominence)[0]
    return peakindex

def getPath(self, documenttype="GISAXS data file (*.cbf);;All Files (*)"):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    path = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",documenttype, options=options)[0]
    return path

def openFile(self):
    path = getPath(self)
    return path

def loadMap(self):
    self.firstRun = True
    self.rect = None
    self.holdVertical.setChecked(False)
    self.holdHorizontal.setChecked(False)
    self.rect = Rectangle((0, 0), 1, 1, alpha=1, fill=None, color="red")
    self.figurecanvas = None
    file = openFile(self)
    path = os.path.dirname(file)
    filename = Path(file).name
    os.chdir(path)
    self.filename = filename
    contents = cbf.read(filename)
    data = contents.data
    self.data = data
    layout = self.maplayout
    self.clearLayout(self.maplayout)
    self.figurecanvas = singlePlotonCanvas(self, layout, data)
    self.figurecanvas[1].canvas.mpl_connect('button_press_event', self.on_press)
    self.figurecanvas[1].canvas.mpl_connect('motion_notify_event', self.on_hover)
    self.figurecanvas[1].canvas.mpl_connect('button_release_event', self.on_release)

    self.figurecanvas[0].ax = plt.gca()
    self.scanX()
    self.holdVertical.setChecked(True)
    self.YonedaScan()
    self.firstRun = False

def plotGraphOnCanvas(self, layout, X, Y, title = "", scale="log", marker = None, revert = False):
    canvas = PlotWidget(xlabel="Detector position (pixels)", ylabel="Intensity (arb. u)",
                        title = "Horizontal Scan")
    figure = canvas.figure
    plotgGraphFigure(X, Y, canvas, revert=revert, title=title)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas

def plotgGraphFigure(X, Y, canvas, filename="", xlim=None, title="", scale="log",marker=None, linestyle="solid",
                     revert = False):
    fig = canvas.theplot
    fig.plot(X, Y, label=filename, linestyle=linestyle, marker=marker)
    if revert:
        fig.invert_xaxis()
    canvas.theplot.set_title(title)
    canvas.theplot.set_xlim(xlim)
    canvas.theplot.set_yscale(scale)

def singlePlotonCanvas(self, layout, data, xlim=None):
    canvas = PlotWidget(xlabel="Horizontal detector position (pixels)", ylabel="Vertical detector position (pixels)",
                        title="GISAXS Data")
    canvas.theplot.set_title("GISAXS Data")
    figure = canvas.figure
    plotFigure(data, canvas, title = "GISAXS Data")
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas

def loadEmpty(self):
    canvas = PlotWidget(xlabel="Horizontal detector position (pixels)", ylabel="Intensity (arb. u)",
                        title = "GISAXS data")
    canvas2 = PlotWidget(xlabel="Horizontal detector position (pixels)", ylabel="Vertical detector position (pixels)",
                        title = "Horizontal scan")

    figure = canvas.figure
    layout = self.maplayout
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(canvas)
    layout.addWidget(self.toolbar)

    layout = self.graphlayout
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(canvas2)
    layout.addWidget(self.toolbar)
    canvas3 = PlotWidget(xlabel="Horizontal detector position (pixels)", ylabel="Intensity (arb. u)",
                        title = "Vertical scan")

    layout.addWidget(canvas3)
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)



def plotFigure(data, canvas, filename="", xlim=None, title="", scale="linear",marker=None, linestyle="solid"):
    fig = canvas.theplot
    fig.imshow(data, cmap='gray_r', norm=LogNorm())
    canvas.theplot.set_title(title)
    canvas.theplot.set_xlim(xlim)
    canvas.theplot.set_yscale(scale)


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, xlabel=None, ylabel='Intensity (arb. u)', title="", scale="linear"):
        super(PlotWidget, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.theplot = self.figure.add_subplot(111)
        self.theplot.set_title(title)
        self.theplot.set_xlabel(xlabel)
        self.theplot.set_ylabel(ylabel)
        self.figure.set_tight_layout(True)