from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import scanning_tools
import settings

def plotGraphOnCanvas(self, layout, X, Y, title = "", scale="log", marker = None, revert = False):
    canvas = PlotWidget(xlabel="In-plane scattering angle 2$\phi{_f}$ (°)", ylabel="Intensity (arb. u)",
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
    canvas = PlotWidget(xlabel="In-plane scattering angle 2$\phi{_f}$ (°)", ylabel="Out-of-plane scattering angle $\\alpha{_f}$",
                        title = title)
    figure = canvas.figure
    plotFigure(data, canvas, title = title)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas

def test():
    pass

def plotFigure(data, canvas, filename="", xlim=None, title="", scale="linear",marker=None, linestyle="solid"):
    fig = canvas.theplot
    y_array = list(range(0, len(data)))
    data = data[::-1]
    x_array = list(range(0, len(data[0])))
    x_theta_f = scanning_tools.convert_x(x_array)
    y_alpha_f = scanning_tools.convert_y(y_array)
    x_min = min(x_theta_f)
    x_max = max(x_theta_f)
    y_min = min(y_alpha_f)
    y_max = max(y_alpha_f)
    cmap = settings.get_cmap()
    fig.imshow(data, cmap=cmap, norm=LogNorm(), origin="lower", extent=[x_min, x_max, y_min, y_max], aspect="auto")



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

