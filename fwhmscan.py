import CallUI
import plottingtools
import scanning_tools
import numpy as np
import json
import os
import gisaxs
import settings
import shutil


def open_fwhmscan_window(self):
    """Opens window with FWHM scan setup."""
    self.fwhmscan_window = CallUI.fwhmscanUI()

    data = self.sampledata.gisaxs_data
    layout = self.fwhmscan_window.map_preview
    self.clearLayout(layout)
    self.previewcanvas = plottingtools.singlePlotonCanvas(self, layout, data, title=self.filename)

    config_path = settings.get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)

    step_size = config.get("fwhmscan_stepsize", float(self.fwhmscan_window.step_size_entry.displayText()))
    width = config.get("fwhmscan_width", float(self.fwhmscan_window.width_entry.displayText()))
    qz_middle = config.get("fwhmscan_qzposition", float(self.fwhmscan_window.qz_pos_entry.displayText()))
    heigth = config.get("fwhmscan_heigth", float(self.fwhmscan_window.heigth_entry.displayText()))
    qy_stop = config.get("fwhmscan_qystop", float(self.fwhmscan_window.qy_stop_entry.displayText()))

    self.fwhmscan_window.step_size_entry.setText(str(step_size))
    self.fwhmscan_window.width_entry.setText(str(width))
    self.fwhmscan_window.qz_pos_entry.setText(str(qz_middle))
    self.fwhmscan_window.heigth_entry.setText(str(heigth))
    self.fwhmscan_window.qy_stop_entry.setText(str(qy_stop))

    self.fwhmscan_window.show()
    self.fwhmscan_window.accepted.connect(lambda: press_fwhmscan(self))


def press_fwhmscan(self):
    save_fwhmscan_settings(self)
    fwhmscan(self)


def save_fwhmscan_settings(self):
    config_path = settings.get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)

    config["fwhmscan_stepsize"] = float(self.fwhmscan_window.step_size_entry.displayText())
    config["fwhmscan_qystop"] = float(self.fwhmscan_window.qy_stop_entry.displayText())
    config["fwhmscan_width"] = float(self.fwhmscan_window.width_entry.displayText())
    config["fwhmscan_qzposition"] = float(self.fwhmscan_window.qz_pos_entry.displayText())
    config["fwhmscan_heigth"] = float(self.fwhmscan_window.heigth_entry.displayText())

    with open("config.json", 'w') as f:
        json.dump(config, f)


def open_fwhmscan_result_window(self, X, Y):
    """Opens results of FWHM scan."""
    self.fwhmscan_result_window = CallUI.fwhmscan_resultUI()
    layout = self.fwhmscan_result_window.fwhm_graph_layout
    self.clearLayout(layout)
    in_plane_label, out_of_plane_label = gisaxs.get_labels()
    self.fwhmscan_result_window.save_button.clicked.connect(lambda: saveFile(self, X, Y))
    plottingtools.plotGraphOnCanvas(self, layout, X, Y, ylabel=r"FWHM (Å$^{-1}$)", xlabel=in_plane_label,
                                    title="FWHM scan", scale="linear", revert=False, marker="o")
    self.fwhmscan_result_window.show()


def saveFile(self, X, Y):
    """Save FWHM scan to file."""
    filename = f"{self.filename[:-4]}_FWHMscan"
    path = self.saveFileDialog(filename=filename, title="Save FWHM scan")
    filename = path[0]
    if not filename.endswith(".txt"):
        filename = filename + ".txt"
    array = np.stack([X, Y], axis=1)
    np.savetxt(filename, array, delimiter="\t")


def _scan_at_qy(self, qy_coordinate, width, qz_middle, heigth):
    """Perform a single vertical scan at a given qy position. Returns (qy, FWHM) or None on failure."""
    x1 = qy_coordinate - width / 2
    x2 = qy_coordinate + width / 2
    y1 = qz_middle + heigth / 2
    y2 = qz_middle - heigth / 2

    self.ROI_scan_rect.extents = [x1, x2, y1, y2]
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
    height = abs(startx - stopx) or 1
    self.sampledata.vertical_scan_y = [v / height for v in intensity_list]
    self.sampledata.remove_background(horizontal=False)
    self.sampledata.remove_zeroes()

    try:
        index_max = np.argmax(self.sampledata.vertical_scan_y)
    except ValueError:
        print(f"Couldn't get a FWHM at qy={qy_coordinate}, skipping")
        return None

    qz = self.sampledata.vertical_scan_x[index_max]
    return find_FWHM(self, position=qz)


def fwhmscan(self):
    """Perform the FWHM scan."""
    step_size = float(self.fwhmscan_window.step_size_entry.displayText())
    qy_stop = float(self.fwhmscan_window.qy_stop_entry.displayText())
    width = float(self.fwhmscan_window.width_entry.displayText())
    qz_middle = float(self.fwhmscan_window.qz_pos_entry.displayText())
    heigth = float(self.fwhmscan_window.heigth_entry.displayText())

    qy_positive = np.arange(0, qy_stop, step_size)
    qy_negative = np.arange(0, -qy_stop, -step_size)

    results_pos = {}
    results_neg = {}

    for qy in qy_positive:
        fwhm = _scan_at_qy(self, qy, width, qz_middle, heigth)
        if fwhm is not None:
            results_pos[qy] = fwhm

    for qy in qy_negative:
        fwhm = _scan_at_qy(self, qy, width, qz_middle, heigth)
        if fwhm is not None:
            results_neg[qy] = fwhm

    FWHM_average = []
    qy_newlist = []
    for qy in qy_positive:
        fwhm_p = results_pos.get(qy)
        fwhm_n = results_neg.get(-qy if qy != 0 else 0)
        if fwhm_p is None or fwhm_n is None:
            continue
        # If one side is near zero, use the other
        if fwhm_p < 0.001:
            fwhm_p = fwhm_n
        if fwhm_n < 0.001:
            fwhm_n = fwhm_p
        if fwhm_p == 0 and fwhm_n == 0:
            continue
        FWHM_average.append((fwhm_p + fwhm_n) / 2)
        qy_newlist.append(qy)

    open_fwhmscan_result_window(self, qy_newlist, FWHM_average)


def find_FWHM(self, position, scan_type="vertical"):
    """Find FWHM of the peak near position."""
    xdata = self.sampledata.vertical_scan_x
    ydata = self.sampledata.vertical_scan_y
    index_max = np.argmax(ydata)
    peak_coordinate = xdata[index_max]

    half_intensity = max(ydata) / 2
    xs = np.sort(xdata)
    ys = np.array(ydata)[np.argsort(xdata)]
    found_left = False
    found_right = False
    FWHM = 0
    mesh_step = 100000

    for i in range(mesh_step):
        t = i / mesh_step
        y_value_left = np.interp(peak_coordinate - t, xs, ys)
        y_value_right = np.interp(peak_coordinate + t, xs, ys)
        if not found_left and y_value_left <= half_intensity:
            left_boundary_value = peak_coordinate - t
            found_left = True
        if not found_right and y_value_right <= half_intensity:
            right_boundary_value = peak_coordinate + t
            found_right = True
        if found_left and found_right:
            FWHM = right_boundary_value - left_boundary_value
            break

    return FWHM
