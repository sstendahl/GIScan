import gisaxs
import numpy as np
import plottingtools
import json
import os
from scipy.signal import find_peaks
import scanning_tools as scan
import settings


def ttheta_f(pp_x, db_x, ps_x, sdd):
    """Convert single horizontal pixel coordinate to angular coordinates"""
    return np.degrees(np.arctan((pp_x - db_x) * ps_x / sdd))


def alpha_f(pp_y, db_y, ps_y, sdd, a_i):
    """Convert single vertical pixel coordinate to angular coordinates"""

    return np.degrees(np.arctan((pp_y - db_y) * ps_y / sdd)) - a_i


def convert_x(pp_x):
    """Convert horizontal pixel positions to angular coordinates"""
    config_path = settings.get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)
    db_x = config["db_x"]
    ps_x = config["ps_x"]
    sdd = config["sdd"]
    theta_array = []
    for datapoint in pp_x:
        theta = ttheta_f(datapoint, db_x, ps_x, sdd)
        theta_array.append(theta)
    return theta_array


def convert_y(pp_y):
    """Convert vertical pixel positions to angular coordinates"""
    config_path = settings.get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)
    db_y = config["db_y"]
    ps_y = config["ps_y"]
    a_i = config["ai"]
    sdd = config["sdd"]
    alpha_array = []
    for datapoint in pp_y:
        alpha = alpha_f(datapoint, db_y, ps_y, sdd, a_i)
        alpha_array.append(alpha)
    return alpha_array


def detector_scan(self):
    """Does a pre-set vertical scan over the qy=0 position at preset coordinates"""

    self.holdHorizontal.setChecked(True)
    self.firstRun = True

    # Note: will probably change these preset values to be relative to the total map limits, in order to avoid
    # out-of-bound issues.
    if settings.get_config("mapping") == "Angular":
        x0 = -0.022
        x1 = 0.022
        y0 = -0.3
        y1 = 2.4

    if settings.get_config("mapping") == "Pixels":
        x0 = 860
        x1 = 877
        y0 = 90
        y1 = 1100

    if settings.get_config("mapping") == "q-space":
        y0 = 0
        y1 = 0.33
        x0 = -0.0033
        x1 = 0.0033

    middleX = (x0 + x1) / 2
    middleY = (y0 + y1) / 2
    height = y1 - y0
    width = x1 - x0

    self.set_entry(height, width, middleX, middleY)
    self.clearLayout(self.horizontal_layout)
    self.clearLayout(self.vertical_layout)
    self.holdVertical.setChecked(False)
    calcOffSpec(self)
    self.setRectangleFromEntry()
    self.firstRun = False


def YonedaScan(self):
    """Does a pre-set horizontal scan near the critical angle for Ni, at preset coordinates"""

    self.holdVertical.setChecked(True)
    if settings.get_config("mapping") == "Angular":
        y0 = 0.255
        y1 = 0.275
        x0 = -1.2
        x1 = 1.2
    if settings.get_config("mapping") == "Pixels":
        y0 = 306
        y1 = 295
        x0 = 600
        x1 = 1140
    if settings.get_config("mapping") == "q-space":
        y0 = 0.075
        y1 = 0.078
        x0 = -0.12
        x1 = 0.12
    height = y1 - y0
    width = x1 - x0
    middleY = (y0 + y1) / 2
    middleX = (x0 + x1) / 2
    self.set_entry(height, width, middleX, middleY)
    self.clearLayout(self.horizontal_layout)
    self.clearLayout(self.vertical_layout)
    self.holdHorizontal.setChecked(False)
    calcOffSpec(self)
    self.setRectangleFromEntry()


def find_specular(self):
    """Does a hori<ontal scan in order to find where the specular signal is located in the qy-plane
    Sets the middleX coordinate to this position (I feel this function is redundant, will take another look at this)
    ."""


    if settings.get_config("mapping") == "Angular":
        y0 = 0.255
        y1 = 0.275
        x0 = -1.2
        x1 = 1.2
    if settings.get_config("mapping") == "Pixels":
        y0 = 306
        y1 = 295
        x0 = 600
        x1 = 1140
    if settings.get_config("mapping") == "q-space":
        y0 = 0.075
        y1 = 0.078
        x0 = -0.10
        x1 = 0.10
    self.clearLayout(self.horizontal_layout)
    self.clearLayout(self.vertical_layout)
    height = y1 - y0
    width = x1 - x0
    middleY = (y0 + y1) / 2
    middleX = (x0 + x1) / 2
    self.set_entry(height, width, middleX, middleY)
    calcOffSpec(self)
    peaks = find_peaks(np.log(self.sampledata.horizontal_scan_y), prominence=2)[0]
    if len(peaks > 0):
        peakindex = peaks[0]
    else:
        peakindex = 0


def calcOffSpec(self, scan = "both"):
    """Perform an off-specular scan in both horizontal and vertical direction"""
    if scan == "both":
        start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=True)
        start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=False)
    elif scan == "vertical":
        start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=False)
    elif scan == "horizontal":
        start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=True)



def start_offspec(self, hold_horizontal, hold_vertical, horizontal=True):
    """Perform the actual off-specular scan in both directions
    Note this function is way too long and should be rewritten probably
    """

    in_plane_label, out_of_plane_label = gisaxs.get_labels()
    startx, stopx, starty, stopy = find_startstop(self)
    intensity_list = calc_cut(self, startx, stopx, starty, stopy, horizontal=horizontal)
    mapping = self.sampledata.mapping
    if horizontal:
        if mapping == "Angular":
            coordinatelist = self.sampledata.get_x_angular()[startx:stopx]
        elif mapping == "q-space":
            coordinatelist = self.sampledata.get_y_qspace()[startx:stopx]
        else:
            coordinatelist = self.sampledata.get_x_pixels()[startx:stopx]
    else:
        if mapping == "Angular":
            coordinatelist = self.sampledata.get_y_angular()[starty:stopy]
        elif mapping == "q-space":
            coordinatelist = self.sampledata.get_z_qspace()[starty:stopy]
        else:
            coordinatelist = self.sampledata.get_y_pixels()[starty:stopy]


    if horizontal and not hold_horizontal:
        self.sampledata.horizontal_scan_x = coordinatelist
        height = abs(starty - stopy)
        intensity_list = [value/height for value in intensity_list]
        self.sampledata.horizontal_scan_y = intensity_list
        self.sampledata.remove_background()
        self.sampledata.remove_zeroes()


    if not horizontal and not hold_vertical:
        self.sampledata.vertical_scan_x = coordinatelist
        height = abs(startx - stopx)
        intensity_list = [value/height for value in intensity_list]
        self.sampledata.vertical_scan_y = intensity_list
        self.sampledata.remove_background(horizontal = False)
        self.sampledata.remove_zeroes()


    # Now the figures are defined and plotted
    if horizontal:
        scan_type = "horizontal"
        title = "Horizontal scan"
        figure = plottingtools.plotGraphOnCanvas(self, self.horizontal_layout, self.sampledata.horizontal_scan_x,
                                                 self.sampledata.horizontal_scan_y, xlabel=in_plane_label, title=title)
        self.horizontalscanfig = figure

    else:
        scan_type = "vertical"
        title = "Vertical scan"

        figure = plottingtools.plotGraphOnCanvas(self, self.vertical_layout, self.sampledata.vertical_scan_x,
                                                 self.sampledata.vertical_scan_y,
                                                 xlabel=out_of_plane_label, title=title,
                                                 revert=False)
        self.verticalscanfig = figure

    figure[1].canvas.mpl_connect('motion_notify_event',
                                 lambda event: self.dragVline(event, scan_type=scan_type))
    figure[1].canvas.mpl_connect('button_press_event', self.pressVline)
    figure[1].canvas.mpl_connect('button_release_event',
                                 lambda event: self.releaseVline(event, scan_type=scan_type))




def calc_cut(self, startx, stopx, starty, stopy, horizontal=True):
    intensity = 0
    intensity_list = []

    if horizontal:
        starti = startx
        stopi = stopx
        startj = starty
        stopj = stopy
    else:
        starti = starty
        stopi = stopy
        startj = startx
        stopj = stopx

    for i in range(starti, stopi):
        for j in range(startj, stopj):
            if horizontal:
                intensity += self.sampledata.gisaxs_data[::-1][j][i]
            else:
                intensity += self.sampledata.gisaxs_data[::-1][i][j]
        intensity_list.append(intensity)
        intensity = 0
    return intensity_list


def get_average_background(self, type_of_ROI = "bg"):
    startx, stopx, starty, stopy = find_startstop(self, type_of_ROI)
    total_intensity = 0
    total_datapoints = 0
    for i in range(startx, stopx):
        for j in range(starty, stopy):
                total_intensity += self.sampledata.gisaxs_data[::-1][j][i]
                total_datapoints += 1
    average = total_intensity / total_datapoints
    return average

def find_startstop(self, type_of_ROI="scan"):
    startx, stopx, starty, stopy = 0, 0, 0, 0

    if type_of_ROI == "scan":
        x0, x1, y0, y1 = self.ROI_scan_rect.extents
    if type_of_ROI == "bg":
        x0, x1, y0, y1 = self.ROI_background_rect.extents
    start = x0
    stop = x1
    found_start = False
    found_stop = False
    if self.sampledata.mapping == "Angular":
        x_array = self.sampledata.get_x_angular()
        y_array = self.sampledata.get_y_angular()
    elif self.sampledata.mapping == "q-space":
        x_array = self.sampledata.get_y_qspace()
        y_array = self.sampledata.get_z_qspace()
    else:
        x_array = self.sampledata.get_x_pixels()
        y_array = self.sampledata.get_y_pixels()

    for index, element in enumerate(x_array):
        if element > min([start, stop]) and not found_start:
            startx = index
            found_start = True
        if element > max([start, stop]) and not found_stop:
            stopx = index
            found_stop = True
            break
    found_start = False

    start = y1
    stop = y0

    for index, element in enumerate(y_array):
        if element > min([start, stop]) and not found_start:
            starty = index
            found_start = True
        if element > max([start, stop]):
            stopy = index
            break
    return startx, stopx, starty, stopy


def find_peak_in_range(self, position, xdata, ydata):
    found_peak = False
    max_x = max(xdata)
    min_x = min(xdata)

    total_range = abs(xdata.index(max_x) - xdata.index(min_x))
    # Will check for a peak within a range the size of about 6.7% of the total area around the clicked point.
    check_range = int((total_range / 15) / 2)
    chosen_point = position
    chosen_index = 0
    for index in range(len(ydata)):
        if xdata[index] > chosen_point:
            chosen_index = index
            break

    chosen_Yrange = ydata[chosen_index - check_range:chosen_index + check_range]
    chosen_Xrange = xdata[chosen_index - check_range:chosen_index + check_range]
    try:
        peakindex = find_peaks(np.log(chosen_Yrange), prominence=1)[0][0]
        found_peak = True
    except IndexError:
        print("Could not find a peak at this position")
        total_index = None
    if found_peak:
        for index in range(len(xdata)):
            if xdata[index] == chosen_Xrange[peakindex]:
                total_index = index
    return total_index


def find_FWHM(self, position, scan_type="vertical"):
    if scan_type == "horizontal":
        xdata = self.sampledata.horizontal_scan_x
        ydata = self.sampledata.horizontal_scan_y
        figure = self.horizontalscanfig[0]
        axes = figure.axes[0]

    if scan_type == "vertical":
        xdata = self.sampledata.vertical_scan_x
        ydata = self.sampledata.vertical_scan_y
        figure = self.verticalscanfig[0]
        axes = figure.axes[0]
    peak_position = find_peak_in_range(self, position, xdata, ydata)
    print(f"Peak position is {peak_position}")
    if peak_position is not None:
        half_intensity = ydata[peak_position] / 2
        # Find left boundary:

        xs = np.sort(xdata)
        ys = np.array(ydata)[np.argsort(xdata)]
        start_position = peak_position
        peak_coordinate = xdata[start_position]

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

        if hasattr(self, 'hline'):
            self.hline.remove()
        self.hline = axes.hlines(y=ydata[peak_position] / 2, xmin=left_boundary_value, xmax=right_boundary_value,
                                 color='r')
        self.verticalscanfig[1].draw()
        self.horizontalscanfig[1].draw()
    else:
        FWHM = 0
    return FWHM
