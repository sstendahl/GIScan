import gisaxs
import numpy as np
import plottingtools
import json
import os
import sys

import scanning_tools as scan
import settings


def ttheta_f(pp_x, db_x, ps_x, sdd):
    return np.degrees(np.arctan((pp_x - db_x) * ps_x / sdd))


def alpha_f(pp_y, db_y, ps_y, sdd, a_i):
    return np.degrees(np.arctan((pp_y - db_y) * ps_y / sdd)) - a_i


def convert_x(pp_x):
    os.chdir(sys.path[0])
    with open('config.json', 'r') as f:
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
    os.chdir(sys.path[0])
    with open('config.json', 'r') as f:
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
    self.holdHorizontal.setChecked(True)
    self.firstRun = True
    if settings.get_config("mapping") == "Angular":
        self.ROI_scan.x0 = -0.022
        self.ROI_scan.x1 = 0.022
        self.ROI_scan.y0 = -0.3
        self.ROI_scan.y1 = 2.4

    if settings.get_config("mapping") == "Pixels":
        self.ROI_scan.x0 = 860
        self.ROI_scan.x1 = 877
        self.ROI_scan.y0 = 90
        self.ROI_scan.y1 = 1100

    if settings.get_config("mapping") == "q-space":
        self.ROI_scan.y0 = 0
        self.ROI_scan.y1 = 0.33
        self.ROI_scan.x0 = -0.0033
        self.ROI_scan.x1 = 0.0033

    self.middleX = (self.ROI_scan.x0 + self.ROI_scan.x1) / 2
    self.middleY = (self.ROI_scan.y0 + self.ROI_scan.y1) / 2
    self.clearLayout(self.graphlayout)
    scan.calcOffSpec(self)
    self.defineRectangle()
    self.drawRectangle()
    self.holdVertical.setChecked(False)
    self.firstRun = False


def YonedaScan(self):
    self.holdVertical.setChecked(True)
    if settings.get_config("mapping") == "Angular":
        self.ROI_scan.y0 = 0.255
        self.ROI_scan.y1 = 0.275
        self.ROI_scan.x0 = -1.2
        self.ROI_scan.x1 = 1.2
    if settings.get_config("mapping") == "Pixels":
        self.ROI_scan.y0 = 306
        self.ROI_scan.y1 = 295
        self.ROI_scan.x0 = 600
        self.ROI_scan.x1 = 1140
    if settings.get_config("mapping") == "q-space":
        self.ROI_scan.y0 = 0.075
        self.ROI_scan.y1 = 0.078
        self.ROI_scan.x0 = -0.12
        self.ROI_scan.x1 = 0.12
    height = self.ROI_scan.y1 - self.ROI_scan.y0
    width = self.ROI_scan.x1 - self.ROI_scan.x0
    self.middleY = (self.ROI_scan.y0 + self.ROI_scan.y1) / 2
    self.middleX = (self.ROI_scan.x0 + self.ROI_scan.x1) / 2
    self.recHeigthEntry.setText(str(float(height)))
    self.recWidthEntry.setText(str(float(width)))
    self.middleXEntry.setText(str(float(self.middleX)))
    self.middleYEntry.setText(str(float(self.middleY)))
    self.defineRectangle()
    self.drawRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)
    self.holdHorizontal.setChecked(False)


def find_specular(self):
    if settings.get_config("mapping") == "Angular":
        self.ROI_scan.y0 = 0.255
        self.ROI_scan.y1 = 0.275
        self.ROI_scan.x0 = -1.2
        self.ROI_scan.x1 = 1.2
    if settings.get_config("mapping") == "Pixels":
        self.ROI_scan.y0 = 306
        self.ROI_scan.y1 = 295
        self.ROI_scan.x0 = 600
        self.ROI_scan.x1 = 1140
    if settings.get_config("mapping") == "q-space":
        self.ROI_scan.y0 = 0.075
        self.ROI_scan.y1 = 0.078
        self.ROI_scan.x0 = -0.10
        self.ROI_scan.x1 = 0.10
    self.defineRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)
    peaks = gisaxs.detectPeak(self, self.sampledata.horizontal_scan_y)
    if len(peaks > 0):
        peakindex = peaks[0]
    else:
        peakindex = 0
    print(self.sampledata.horizontal_scan_x)
    self.middleX = self.sampledata.horizontal_scan_x[peakindex]


def calcOffSpec(self):
    start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=True)
    start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=False)


def start_offspec(self, hold_horizontal, hold_vertical, horizontal=True):
    in_plane_label, out_of_plane_label = gisaxs.get_labels()

    if self.firstRun == False:
        self.ROI_scan.x0 = float(self.middleX - float(self.recWidthEntry.displayText()) / 2)
        self.ROI_scan.y0 = float(self.middleY - float(self.recHeigthEntry.displayText()) / 2)
        self.ROI_scan.x1 = float(self.middleX + float(self.recWidthEntry.displayText()) / 2)
        self.ROI_scan.y1 = float(self.middleY + float(self.recHeigthEntry.displayText()) / 2)

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
        self.sampledata.horizontal_scan_y = intensity_list
        height = abs(starty - stopy)
        self.sampledata.remove_background(height)
        self.sampledata.remove_zeroes()


    if not horizontal and not hold_vertical:
        self.sampledata.vertical_scan_x = coordinatelist
        self.sampledata.vertical_scan_y = intensity_list
        height = abs(startx - stopx)
        self.sampledata.remove_background(height, horizontal = False)
        self.sampledata.remove_zeroes()


    layout = self.graphlayout

    if horizontal:
        scan_type = "horizontal"
        title = "Horizontal scan"
        figure = plottingtools.plotGraphOnCanvas(self, layout, self.sampledata.horizontal_scan_x,
                                                 self.sampledata.horizontal_scan_y, xlabel=in_plane_label, title=title)
        self.horizontalscanfig = figure

    else:
        scan_type = "vertical"
        title = "Vertical scan"

        figure = plottingtools.plotGraphOnCanvas(self, layout, self.sampledata.vertical_scan_x,
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


def get_average(self, type_of_ROI = "bg"):
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
        ROI = self.ROI_scan
    if type_of_ROI == "bg":
        ROI = self.ROI_background
    start = ROI.x0
    stop = ROI.x1
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

    start = ROI.y1
    stop = ROI.y0

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
        peakindex = gisaxs.detectPeak(self, chosen_Yrange, prominence=1)[0]
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
    if peak_position is not None:
        half_intensity = ydata[peak_position] / 2
        # Find left boundary:

        xs = np.sort(xdata)
        ys = np.array(ydata)[np.argsort(xdata)]
        start_position = peak_position
        peak_coordinate = xdata[start_position]

        found_left = False
        found_right = False
        mesh_step = 1000000

        # Will optimize this a bit
        for index in range(mesh_step):
            index = index / (mesh_step / 200)
            y_value_left = np.interp(peak_coordinate - index, xs, ys)
            y_value_right = np.interp(peak_coordinate + index, xs, ys)
            if found_left == False and y_value_left <= half_intensity:
                left_boundary_value = peak_coordinate - index
                found_left = True
            if found_right == False and y_value_right <= half_intensity:
                right_boundary_value = peak_coordinate + index
                found_right = True
            if found_left == True and found_right == True:
                break

        FWHM = right_boundary_value - left_boundary_value
        if hasattr(self, 'hline'):
            self.hline.remove()
        step_size = abs(xdata[1] - xdata[0])
        self.hline = axes.hlines(y=ydata[peak_position] / 2, xmin=left_boundary_value, xmax=right_boundary_value,
                                 color='r')
        self.verticalscanfig[1].draw()
        self.horizontalscanfig[1].draw()
    else:
        FWHM = 0
    return FWHM
