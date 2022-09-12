import CallUI
import plottingtools

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
    pass
