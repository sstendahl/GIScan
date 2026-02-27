from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import gisaxs
import settings


def plotGraphOnCanvas(self, layout, X, Y, xlabel=r"In-plane scattering angle 2$\phi{_f}$ (°)",
                      ylabel="Intensity (arb. u)", title="", scale="log", marker=None, revert=False):
    canvas = PlotWidget(xlabel=xlabel, ylabel=ylabel, title=title)
    figure = canvas.figure
    plotGraphFigure(X, Y, canvas, revert=revert, title=title, marker=marker, scale=scale)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas


def plotGraphFigure(X, Y, canvas, filename="", xlim=None, title="", scale="log", marker=None, linestyle="solid",
                    revert=False):
    fig = canvas.ax
    fig.plot(X, Y, label=filename, linestyle=linestyle, marker=marker)
    if revert:
        fig.invert_xaxis()
    canvas.ax.set_title(title)
    canvas.ax.set_xlim(xlim)
    canvas.ax.set_yscale(scale)


def singlePlotonCanvas(self, layout, data, title="GISAXS Data", style="bmh"):
    in_plane_label, out_of_plane_label = gisaxs.get_labels()
    canvas = PlotWidget(xlabel=in_plane_label, ylabel=out_of_plane_label, title=title, style=style)
    figure = canvas.figure
    plotFigure(self, data, canvas, title=title)
    layout.addWidget(canvas)
    figurecanvas = [figure, canvas]
    self.toolbar = NavigationToolbar(canvas, self)
    layout.addWidget(self.toolbar)
    return figurecanvas


def plotFigure(self, data, canvas, title=""):
    fig = canvas.ax
    data = data[::-1]
    x_array = list(range(0, len(data[0])))
    y_array = list(range(0, len(data)))

    if self.sampledata.mapping == "Angular":
        x_array = self.sampledata.get_x_angular()
        y_array = self.sampledata.get_y_angular()
    elif self.sampledata.mapping == "q-space":
        x_array = self.sampledata.get_y_qspace()
        y_array = self.sampledata.get_z_qspace()

    x_min = min(x_array)
    x_max = max(x_array)
    y_min = min(y_array)
    y_max = max(y_array)
    cbar = settings.get_config("colorbar")
    cmap = settings.get_config("cmap")
    gisaxs_map = fig.imshow(data, cmap=cmap, norm=colors.SymLogNorm(linthresh=5), origin="lower",
                            extent=[x_min, x_max, y_min, y_max], aspect="auto")
    if cbar:
        pos = settings.get_config("cbar_pos").lower()
        canvas.figure.colorbar(gisaxs_map, location=pos)


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, xlabel="", ylabel="", title="", style="bmh"):
        if settings.get_config("dark_graphs"):
            plt.style.use('dark_background')
        else:
            plt.style.use(style)
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title, fontsize=12)
        self.figure.set_tight_layout(True)
        self.ax.set_xlabel(xlabel, fontsize=11)
        self.ax.set_ylabel(ylabel, fontsize=11)
        super(PlotWidget, self).__init__(self.figure)
