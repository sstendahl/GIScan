import CallUI
import plottingtools
import scanning_tools
import numpy as np
import gisaxs


def open_fwhmscan_window(self):
    """Opens settings dialog."""
    self.fwhmscan_window = CallUI.fwhmscanUI()

    data = self.sampledata.gisaxs_data
    layout = self.fwhmscan_window.map_preview
    self.clearLayout(layout)
    self.figurecanvas = plottingtools.singlePlotonCanvas(self, layout, data, title=self.filename)
    self.fwhmscan_window.show()
    self.fwhmscan_window.accepted.connect(lambda: fwhmscan(self))


def open_fwhmscan_result_window(self, X, Y):
    """Opens settings dialog."""
    self.fwhmscan_result_window = CallUI.fwhmscan_resultUI()
    layout = self.fwhmscan_result_window.fwhm_graph_layout
    self.clearLayout(layout)
    in_plane_label, out_of_plane_label = gisaxs.get_labels()
    self.fwhmscan_result_window.save_button.clicked.connect(lambda: saveFile(self, X, Y))
    figure = plottingtools.plotGraphOnCanvas(self, layout, X, Y, ylabel="FWHM (Å-1)", xlabel=out_of_plane_label,
                                             title="FWHM scan", scale="linear",
                                             revert=False, marker = "o")
    self.fwhmscan_result_window.show()

def saveFile(self, X, Y):
    filename = f"{self.filename[:-4]}_FWHMscan"
    path = self.saveFileDialog(filename = filename, title="Save FWHM scan")
    filename = path[0]
    if filename[-4:] != ".txt":
        filename = filename + ".txt"
    array = np.stack([X, Y], axis=1)
    np.savetxt(filename, array, delimiter="\t")


def fwhmscan(self):
    qy_coordinate = 0
    FWHM_list = []
    FWHM_listminus = []
    qy_list = []
    qy_listminus = []
    skiplist = []
    step_size = float(self.fwhmscan_window.step_size_entry.displayText())
    qy_stop = float(self.fwhmscan_window.qy_stop_entry.displayText())
    width = float(self.fwhmscan_window.width_entry.displayText())

    while qy_coordinate < qy_stop:
        x1 = qy_coordinate - width/2
        x2 = qy_coordinate + width/2
        self.ROI_scan_rect.extents = [x1, x2, 0.10, 0.2]
        startx, stopx, starty, stopy = scanning_tools.find_startstop(self)
        intensity_list = scanning_tools.calc_cut(self, startx, stopx, starty, stopy, horizontal=False)
        mapping = self.sampledata.mapping
        if mapping == "Angular":
            coordinatelist = self.sampledata.get_y_angular()[starty:stopy]
        elif mapping == "q-space":
            coordinatelist = self.sampledata.get_z_qspace()[starty:stopy]
        else:
            coordinatelist = self.sampledata.get_y_pixels()[starty:stopy]

        self.sampledata.vertical_scan_x = coordinatelist
        height = abs(startx - stopx)
        intensity_list = [value / height for value in intensity_list]
        self.sampledata.vertical_scan_y = intensity_list
        self.sampledata.remove_background(horizontal=False)
        self.sampledata.remove_zeroes()
        try:
            index_max = np.argmax(self.sampledata.vertical_scan_y)
        except ValueError:
            print("Couldn't get a FWHM at this position, skipping coordinate")
            FWHM_list.append(0)
            skiplist.append(qy_coordinate)
            qy_list.append(qy_coordinate)
            qy_coordinate += step_size
            continue

        qz = self.sampledata.vertical_scan_x[index_max]

        FWHM = find_FWHM(self, position=qz)
        FWHM_list.append(FWHM)
        qy_list.append(qy_coordinate)
        qy_coordinate += step_size

    qy_coordinate = 0
    while qy_coordinate > -qy_stop:
        x1 = qy_coordinate - width/2
        x2 = qy_coordinate + width/2
        self.ROI_scan_rect.extents = [x1, x2, 0.10, 0.2]
        startx, stopx, starty, stopy = scanning_tools.find_startstop(self)
        intensity_list = scanning_tools.calc_cut(self, startx, stopx, starty, stopy, horizontal=False)
        mapping = self.sampledata.mapping
        if mapping == "Angular":
            coordinatelist = self.sampledata.get_y_angular()[starty:stopy]
        elif mapping == "q-space":
            coordinatelist = self.sampledata.get_z_qspace()[starty:stopy]
        else:
            coordinatelist = self.sampledata.get_y_pixels()[starty:stopy]

        self.sampledata.vertical_scan_x = coordinatelist
        height = abs(startx - stopx)
        intensity_list = [value / height for value in intensity_list]
        self.sampledata.vertical_scan_y = intensity_list
        self.sampledata.remove_background(horizontal=False)
        self.sampledata.remove_zeroes()
        try:
            index_max = np.argmax(self.sampledata.vertical_scan_y)
        except ValueError:
            print("Couldn't get a FWHM at this position, skipping coordinate")
            FWHM_listminus.append(0)
            qy_listminus.append(qy_coordinate)
            skiplist.append(qy_coordinate)
            qy_coordinate -= step_size
            continue

        qz = self.sampledata.vertical_scan_x[index_max]
        FWHM = find_FWHM(self, position=qz)
        FWHM_listminus.append(FWHM)
        #Temporary solution, fix before stable release!
        qy_listminus.append(qy_coordinate)
        qy_coordinate -= step_size

    FWHM_average = []
    qy_newlist = []
    for index in range(len(qy_list)):
        if (qy_list[index] not in skiplist) and (qy_listminus[index] not in skiplist):
            if FWHM_list[index] < 0.001:
                FWHM_list[index] = FWHM_listminus[index]
            if FWHM_listminus[index] < 0.001:
                FWHM_listminus[index] = FWHM_list[index]
            if not (FWHM_list[index] == 0 and FWHM_listminus[index] == 0):
                FWHM = (FWHM_list[index] + FWHM_listminus[index]) / 2
                FWHM_average.append(FWHM)
                qy_newlist.append(qy_list[index])

    open_fwhmscan_result_window(self, qy_newlist, FWHM_average)


def find_FWHM(self, position, scan_type="vertical"):
    """PLACEHOLDER FUNCTION! WORKS BUT VERY UGLY, DO NOT USE FOR STABLE RELEASE"""
    xdata = self.sampledata.vertical_scan_x
    ydata = self.sampledata.vertical_scan_y
    index_max = np.argmax(self.sampledata.vertical_scan_y)
    qz = self.sampledata.vertical_scan_x[index_max]

    peak_coordinate = qz
    FWHM = 0
    half_intensity = max(ydata) / 2
    xs = np.sort(xdata)
    ys = np.array(ydata)[np.argsort(xdata)]
    found_left = False
    found_right = False
    mesh_step = 100000


    # Will optimize this a bit
    for index in range(mesh_step):
        index = index / (mesh_step)
        y_value_left = np.interp(peak_coordinate - index, xs, ys)
        y_value_right = np.interp(peak_coordinate + index, xs, ys)
        if found_left == False and y_value_left <= half_intensity:
            left_boundary_value = peak_coordinate - index
            found_left = True
        if found_right == False and y_value_right <= half_intensity:
            right_boundary_value = peak_coordinate + index
            found_right = True

        if found_left == True and found_right == True:
            FWHM = right_boundary_value - left_boundary_value

            break

    return FWHM
