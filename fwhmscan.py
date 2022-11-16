import CallUI
import plottingtools
import scanning_tools

def open_fwhmscan_window(self):
    """Opens settings dialog."""
    self.fwhmscan_window = CallUI.fwhmscanUI()

    data = self.sampledata.gisaxs_data
    layout = self.fwhmscan_window.map_preview
    self.clearLayout(layout)
    self.figurecanvas = plottingtools.singlePlotonCanvas(self, layout, data, title=self.filename)

    self.fwhmscan_window.show()
    self.fwhmscan_window.accepted.connect(lambda: fwhmscan(self))

def fwhmscan(self):
    self.ROI_scan_rect.extents = [-0.01, 0.01, 0.10, 0.2]
    startx, stopx, starty, stopy = scanning_tools.find_startstop(self)
    intensity_list = scanning_tools.calc_cut(self, startx, stopx, starty, stopy, horizontal=False)