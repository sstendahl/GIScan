import gisaxs
import numpy as np
import plottingtools

def ttheta_f(pp_x, db_x, ps_x, sdd):
    return np.degrees(np.arctan((pp_x - db_x) * ps_x / sdd))

def alpha_f(pp_y, db_y, ps_y, sdd, a_i):
    return np.degrees(np.arctan((pp_y - db_y) * ps_y / sdd)) - a_i

def convert_x(pp_x):
    db_x = get_settings()["db_x"]
    ps_x = get_settings()["ps_x"]
    sdd = get_settings()["sdd"]
    theta_array = []
    for datapoint in pp_x:
        theta = ttheta_f(datapoint, db_x, ps_x, sdd)
        theta_array.append(theta)
    return theta_array


def convert_y(pp_y):
    db_y = get_settings()["db_y"]
    ps_y = get_settings()["ps_y"]
    a_i = get_settings()["a_i"]
    sdd = get_settings()["sdd"]
    alpha_array = []
    for datapoint in pp_y:
        alpha = alpha_f(datapoint, db_y, ps_y, sdd, a_i)
        alpha_array.append(alpha)
    return alpha_array


def get_settings():
    a_i = 0.40
    sdd = 3850
    db_y = 40
   # db_y = 1382 #Could also be 1300, please check!
    db_x = 869
    ps_x = 0.172
    ps_y = 0.172
    return{"a_i": a_i, "sdd": sdd, "db_y": db_y, "db_x": db_x, "ps_x": ps_x, "ps_y": ps_y}

def detector_scan(self):
    self.holdHorizontal.setChecked(True)
    self.firstRun = True
    self.y0 = None
    self.y1 = None
    self.x0 = -0.1
    self.x1 = 0.1
    scanX(self)
    self.y0 = None
    self.y1 = None
    self.middleX = None
    self.middleY = None
    self.y0 = -0.2
    self.y1 = 2.3
    self.defineRectangle()
    self.drawRectangle()
    self.firstRun = False


def YonedaScan(self):
    self.holdVertical.setChecked(True)
    self.y0 = 0.22
    self.y1 = 0.32
    self.x0 = -1.25
    self.x1 = 1.25
    self.middleY = (self.y0 + self.y1) / 2
    self.middleX = (self.x0 + self.x1) / 2
    self.recHeigthEntry.setText(str(0.2))
    self.recWidthEntry.setText(str(2.5))
    self.middleXEntry.setText(str(int(self.middleX)))
    self.middleYEntry.setText(str(int(self.middleY)))
    self.defineRectangle()
    self.drawRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)




def findSpecular(self):
    self.y0 = 0.7
    self.y1 = 0.8
    self.x0 = -1
    self.x1 = 1
    self.middleY = (self.y0 + self.y1) / 2
    self.middleX = (self.x0 + self.x1) / 2
    self.defineRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)
    peakindex = gisaxs.detectPeak(self, self.sampledata.horizontal_scan_y)[0]
    self.middleX = self.sampledata.horizontal_scan_x[peakindex]


def scanX(self):
    findSpecular(self)
    self.y0 = -0.45
    self.y1 = 2
    heigth = self.y1 - self.y0
    self.x0 = self.middleX - 0.05
    self.x1 = self.middleX + 0.05
    width = self.middleX
    self.defineRectangle(width=width, heigth=heigth)
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)


def calcOffSpec(self):
    start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=True)
    start_offspec(self, self.holdHorizontal.isChecked(), self.holdVertical.isChecked(), horizontal=False)

    # startVertical(self, self.holdVertical.isChecked())


def start_offspec(self, hold_horizontal, hold_vertical, horizontal=True):
    if self.firstRun == False:
        self.x0 = float(self.middleX - float(self.recWidthEntry.displayText()) / 2)
        self.y0 = float(self.middleY - float(self.recHeigthEntry.displayText()) / 2)
        self.x1 = float(self.middleX + float(self.recWidthEntry.displayText()) / 2)
        self.y1 = float(self.middleY + float(self.recHeigthEntry.displayText()) / 2)

    startstop = find_startstop(self)
    startx = startstop[0]
    stopx = startstop[1]
    starty = startstop[2]
    stopy = startstop[3]
    intensity_list = calc_cut(self, startx, stopx, starty, stopy, horizontal=horizontal)

    if horizontal:
        coordinatelist = self.sampledata.get_x_angular()[startx:stopx]
    else:
        coordinatelist = self.sampledata.get_y_angular()[starty:stopy]

    data = removeZeroes(self, intensity_list, coordinatelist)

    if horizontal and not hold_horizontal:
        self.sampledata.horizontal_scan_x = data[1]
        self.sampledata.horizontal_scan_y = data[0]
    if not horizontal and not hold_vertical:
        self.sampledata.vertical_scan_x = data[1]
        self.sampledata.vertical_scan_y = data[0]

    layout = self.graphlayout

    if horizontal:
        scan_type = "horizontal"
        title = "Horizontal scan"
        figure = plottingtools.plotGraphOnCanvas(self, layout, self.sampledata.horizontal_scan_x,
                                                                 self.sampledata.horizontal_scan_y, title=title)
        self.horizontalscanfig = figure

    else:
        scan_type = "vertical"
        title = "Vertical scan"
        figure = plottingtools.plotGraphOnCanvas(self, layout, self.sampledata.vertical_scan_x,
                                                               self.sampledata.vertical_scan_y, title=title,
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


def find_startstop(self):
    start = float(self.x0)
    stop = float(self.x1)
    found_start = False
    found_stop = False
    for index, element in enumerate(self.sampledata.get_x_angular()):
        if element > min([start, stop]) and not found_start:
            startx = index
            found_start = True
        if element > max([start, stop]) and not found_stop:
            stopx = index
            found_stop = True
            break
    found_start = False

    start = float(self.y1)
    stop = float(self.y0)

    for index, element in enumerate(self.sampledata.get_y_angular()):
        if element > min([start, stop]) and not found_start:
            starty = index
            found_start = True
        if element > max([start, stop]):
            stopy = index
            break
    return [startx, stopx, starty, stopy]


def removeZeroes(self, intensity_list, coordinatelist):
    new_list = []
    new_coordinatelist = []
    for index in range(len(intensity_list)):
        if intensity_list[index] > intensity_list[-1] / 3:
            new_list.append(intensity_list[index])
            new_coordinatelist.append(coordinatelist[index])
    return [new_list, new_coordinatelist]


def find_peak_in_range(self, position, xdata, ydata):
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

    peakindex = gisaxs.detectPeak(self, chosen_Yrange, prominence=1)[0]
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

    half_intensity = ydata[peak_position] / 2
    # Find left boundary:

    xs = np.sort(xdata)
    ys = np.array(ydata)[np.argsort(xdata)]
    start_position = peak_position
    peak_coordinate = xdata[start_position]

    found_left = False
    found_right = False
    mesh_step = 1000000

    #Will optimize this a bit
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
    self.hline = axes.hlines(y=ydata[peak_position] / 2, xmin=left_boundary_value, xmax=right_boundary_value, color='r')
    self.verticalscanfig[1].draw()
    self.horizontalscanfig[1].draw()
    return FWHM
