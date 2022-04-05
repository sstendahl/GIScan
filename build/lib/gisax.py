from PyQt5.QtWidgets import QFileDialog, QShortcut
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle

def getPath(self, documenttype="Data files (*.txt *.xy *.dat);;All Files (*)"):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    path = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",documenttype, options=options)[0]
    return path

def openFile(self):
    path = getPath(self)
    filename = Path(path).name
    return filename

def loadMap(self):
    self.rect = None
    self.rect = Rectangle((0, 0), 1, 1, alpha=1, fill=None, color="red")
    self.figurecanvas = None
    filename = openFile(self)
    self.filename = filename
    data = np.genfromtxt(filename)
    x_list = data[:, 1]
    y_list = data[:, 0]
    z_list = data[:, 2]
    self.xlist = x_list
    self.ylist = y_list
    z = z_list.reshape(int(max(y_list)) + 1, int(max(x_list)) + 1)
    self.z = z
    layout = self.maplayout
    self.clearLayout(self.maplayout)
    self.figurecanvas = singlePlotonCanvas(self, layout, y_list, x_list, z)
    self.figurecanvas[1].canvas.mpl_connect('button_press_event', self.on_press)
    self.figurecanvas[1].canvas.mpl_connect('button_release_event', self.on_release)
    self.figurecanvas[1].canvas.mpl_connect('motion_notify_event', self.on_hover)

    self.figurecanvas[0].ax = plt.gca()

def plotGraphOnCanvas(self, layout, X, Y, title = "", scale="log", marker = None):
    canvas = PlotWidget(xlabel="Relative detector position (pixels)", ylabel="Intensity (arb. u)",
                        title = "Horizontal Scan")
    figure = canvas.figure
    plotgGraphFigure(X, Y, canvas, title=title)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas

def plotgGraphFigure(X, Y, canvas, filename="", xlim=None, title="", scale="log",marker=None, linestyle="solid"):
    fig = canvas.theplot
    fig.plot(X, Y, label=filename, linestyle=linestyle, marker=marker)
    canvas.theplot.set_title(title)
    canvas.theplot.set_xlim(xlim)
    canvas.theplot.set_yscale(scale)

def singlePlotonCanvas(self, layout, X, Y, Z, xlim=None):
    canvas = PlotWidget(xlabel="Horizontal detector position (pixels)", ylabel="Vertical detector position (pixels)", title="GISAXS Data")
    canvas.theplot.set_title("GISAXS Data")
    figure = canvas.figure
    plotFigure(X, Y, Z, canvas, title = "GISAXS Data")
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



def plotFigure(X, Y, Z, canvas, filename="", xlim=None, title="", scale="linear",marker=None, linestyle="solid"):
    fig = canvas.theplot
    fig.imshow(Z, extent=(np.amin(Y), np.amax(Y), np.amin(X), np.amax(X)),
                        norm=LogNorm(),
                        aspect='auto', cmap="gray_r")
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