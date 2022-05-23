from matplotlib.figure import Figure
import matplotlib.colors as colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import gisaxs
import settings

def plotGraphOnCanvas(self, layout, X, Y, xlabel="In-plane scattering angle 2$\phi{_f}$ (°)", title = "", scale="log", marker = None, revert = False):
    canvas = PlotWidget(xlabel=xlabel, ylabel="Intensity (arb. u)",
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

def singlePlotonCanvas(self, layout, data, ylabel = "", xlim=None, title = "GISAXS Data"):
    in_plane_label, out_of_plane_label = gisaxs.get_labels()
    canvas = PlotWidget(xlabel=in_plane_label, ylabel=out_of_plane_label,
                        title = title)
    figure = canvas.figure
    plotFigure(self, data, canvas, title = title)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas

def test():
    pass

def plotFigure(self, data, canvas, filename="", xlim=None, title="", scale="linear",marker=None, linestyle="solid"):
    fig = canvas.theplot
    y_array = list(range(0, len(data)))
    data = data[::-1]
    x_array = list(range(0, len(data[0])))
    if self.sampledata.mapping == "Angular":
        x_array = self.sampledata.get_x_angular()
        y_array = self.sampledata.get_y_angular()
    if self.sampledata.mapping == "q-space":
        x_array = self.sampledata.get_y_qspace()
        y_array = self.sampledata.get_z_qspace()
    else:
        pass
    x_min = min(x_array)
    x_max = max(x_array)
    y_min = min(y_array)
    y_max = max(y_array)
    cbar = settings.get_config("colorbar")
    cmap = settings.get_config("cmap")
    #gisaxs_map = fig.contour(data, levels=200, cmap= cmap, locator=ticker.LogLocator(base=2), origin="lower", extent=[x_min, x_max, y_min, y_max], aspect="auto")
    gisaxs_map = fig.imshow(data, cmap=cmap, norm=colors.SymLogNorm(linthresh=5, base=2), origin="lower", extent=[x_min, x_max, y_min, y_max], aspect="auto")
    if cbar:
        pos = settings.get_config("cbar_pos").lower()
        canvas.figure.colorbar(gisaxs_map, location=pos)


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, xlabel="", ylabel="", title="", scale="linear"):
        super(PlotWidget, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.theplot = self.figure.add_subplot(111)
        self.theplot.set_title(title)
        self.figure.set_tight_layout(True)
        self.theplot.set_xlabel(xlabel)
        self.theplot.set_ylabel(ylabel)

