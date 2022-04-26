import gisax
import numpy as np
import roi
from sample import Sample

def YonedaScan(self):
    self.y0 = 1370
    self.y1 = 1375
    self.x0 = 369
    self.x1 = 1369
    self.middleY = (self.y0 + self.y1) / 2
    self.middleX = (self.x0 + self.x1) / 2
    self.recHeigthEntry.setText(str(5))
    self.recWidthEntry.setText(str(1000))
    self.middleXEntry.setText(str(int(self.middleX)))
    self.middleYEntry.setText(str(int(self.middleY)))
    self.defineRectangle()
    self.drawRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)


def findSpecular(self):
    self.y0 = 1450
    self.y1 = 1500
    self.x0 = 550
    self.x1 = 1200
    self.middleY = (self.y0 + self.y1) / 2
    self.middleX = (self.x0 + self.x1) / 2
    self.defineRectangle()
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)
    peakindex = gisax.detectPeak(self, self.sampledata.horizontal_scan_y)[0]
    self.middleX = self.sampledata.horizontal_scan_x[peakindex]


def scanX(self):
    findSpecular(self)
    self.y0 = 500
    self.y1 = 1600
    heigth = self.y1 - self.y0
    self.x0 = self.middleX - 5
    self.x1 = self.middleX + 5
    width = self.middleX
    self.defineRectangle(width=width, heigth=heigth)
    self.clearLayout(self.graphlayout)
    calcOffSpec(self)


def calcOffSpec(self):
    startHorizontal(self, self.holdHorizontal.isChecked())
    startVertical(self, self.holdVertical.isChecked())

def startHorizontal(self, hold_horizontal):
    if hold_horizontal == False:
        if self.firstRun == False:
            self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
            self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
            self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
            self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)

        startstop = find_startstop(self)
        startx = startstop[0]
        stopx = startstop[1]
        starty = startstop[2]
        stopy = startstop[3]

        intensity_list = calcHorizontal(self, startx, stopx, starty, stopy)
        coordinatelist = list(range(startx, stopx))
        data = removeZeroes(self, intensity_list, coordinatelist)
        self.sampledata.horizontal_scan_x = data[1]
        self.sampledata.horizontal_scan_y = data[0]


    layout = self.graphlayout
    self.horizontalscanfig = gisax.plotGraphOnCanvas(self, layout, self.sampledata.horizontal_scan_x, self.sampledata.horizontal_scan_y, title="Horizontal scan")
    self.horizontalscanfig[1].canvas.mpl_connect('motion_notify_event', lambda event: self.dragVline(event, scan_type="horizontal"))
    self.horizontalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
    self.horizontalscanfig[1].canvas.mpl_connect('button_release_event', lambda event: self.releaseVline(event, scan_type="horizontal"))

def calcHorizontal(self, startx, stopx, starty, stopy):
    intensity = 0
    intensity_list = []
    for i in range(startx, stopx):
        for j in range(starty, stopy):
            intensity += self.sampledata.gisaxs_data[j][i]
        intensity_list.append(intensity)
        intensity = 0
    return intensity_list



def find_startstop(self):
    start = int(self.x0)
    stop = int(self.x1)
    startx = min([start, stop])
    stopx = max([start, stop])
    start = int(self.y1)
    stop = int(self.y0)
    starty = min([start, stop])
    stopy = max([start, stop])
    return [startx, stopx, starty, stopy]

def startVertical(self, hold_vertical):
    if hold_vertical == False:
        if self.firstRun == False:
            self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
            self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
            self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
            self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)
        startstop = find_startstop(self)
        startx = startstop[0]
        stopx = startstop[1]
        starty = startstop[2]
        stopy = startstop[3]
        intensity_list = calcVertical(self, startx, stopx, starty, stopy)
        coordinatelist = list(range(min([int(self.y0), int(self.y1)]), max([int(self.y0), int(self.y1)])))
        data = removeZeroes(self, intensity_list, coordinatelist)
        self.sampledata.vertical_scan_x = data[1]
        self.sampledata.vertical_scan_y = data[0]
    layout = self.graphlayout

    self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, self.sampledata.vertical_scan_x, self.sampledata.vertical_scan_y, title="Vertical scan", revert = True)
    self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', lambda event: self.dragVline(event, scan_type="vertical"))
    self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
    self.verticalscanfig[1].canvas.mpl_connect('button_release_event', lambda event: self.releaseVline(event, scan_type="vertical"))

def calcVertical(self, startx, stopx, starty, stopy):
    intensity = 0
    intensity_list = []
    for i in range(starty, stopy):
        for j in range(startx, stopx):
            intensity += self.sampledata.gisaxs_data[i][j]
        intensity_list.append(intensity)
        intensity = 0
    return intensity_list


def removeZeroes(self, intensity_list, coordinatelist):
    new_list = []
    new_coordinatelist = []
    for index in range(len(intensity_list)):
        if intensity_list[index] > intensity_list[0]/2:
            new_list.append(intensity_list[index])
            new_coordinatelist.append(coordinatelist[index])
    return [new_list, new_coordinatelist]


def find_peak_in_range(self, position, xdata, ydata):
    total_range = max(xdata) - min(xdata)
    # Will check for a peak within a range the size of about 6.7% of the total area around the clicked point.
    check_range = int((total_range / 15) / 2)
    chosen_point = int(position)
    chosen_index = 0
    for index in range(len(ydata)):
        if xdata[index] == chosen_point:
            chosen_index = index

    chosen_Yrange = ydata[chosen_index - check_range:chosen_index + check_range]
    chosen_Xrange = xdata[chosen_index - check_range:chosen_index + check_range]

    peakindex = gisax.detectPeak(self, chosen_Yrange, prominence = 1)[0]
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
        canvas = self.horizontalscanfig[1]

    if scan_type == "vertical":
        xdata = self.sampledata.vertical_scan_x
        ydata = self.sampledata.vertical_scan_y
        figure = self.verticalscanfig[0]
        axes = figure.axes[0]
        canvas = self.verticalscanfig[1]
    peak_position = find_peak_in_range(self, position, xdata, ydata)


    half_intensity = ydata[peak_position]/2
    #Find left boundary:

    xs = np.sort(xdata)
    ys = np.array(ydata)[np.argsort(xdata)]
    start_position = peak_position
    peak_coordinate = xdata[start_position]

    found_left = False
    found_right = False
    mesh_step = 1000000

    for index in range(mesh_step):
        index = index/(mesh_step / 200)
        y_value_left = np.interp(peak_coordinate-index, xs, ys)
        y_value_right = np.interp(peak_coordinate+index, xs, ys)
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
    self.hline = axes.hlines(y=ydata[peak_position]/2, xmin=left_boundary_value, xmax=right_boundary_value, color='r')
    self.verticalscanfig[1].draw()
    self.horizontalscanfig[1].draw()
    return FWHM