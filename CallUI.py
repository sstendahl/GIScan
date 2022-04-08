#CallUI.py
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import gisax
from scipy.interpolate import interp1d
Ui_MainWindow, QtBaseClass = uic.loadUiType("form.ui")



class CallUI(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.connectActions()
        self.clicked = False
        self.x0 = None
        self.y0 = None
        self.middleX = None
        self.middleY = None
        self.x1 = None
        self.y1 = None
        gisax.loadEmpty(self)


    def connectActions(self):
        # Connect File actions
        self.load_button.clicked.connect(lambda: gisax.loadMap(self))
        self.saveVertical.clicked.connect(lambda: self.saveFile(horizontal=False))
        self.saveHorizontal.clicked.connect(lambda: self.saveFile(horizontal=True))
        self.setRec.clicked.connect(lambda: self.setRectangleFromEntry())
        self.yoneda_button.clicked.connect(lambda: self.pressYoneda())
        self.detector_button.clicked.connect(lambda: self.pressDetector())
        self.findFWHM_button.clicked.connect(lambda: self.press_FWHM_button())

    def press_FWHM_button(self):
        self.dragButton.setChecked(False)

    def pressYoneda(self):
        self.firstRun = True
        self.scanX()
        self.holdVertical.setChecked(True)
        self.y0 = 1370
        self.y1 = 1375
        self.x0 = 369
        self.x1 = 1369
        self.middleY = (self.y0 + self.y1)/2
        self.middleX = (self.x0+self.x1)/2
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()
        self.defineRectangle()
        self.drawRectangle()
        self.firstRun = False

    def pressDetector(self):
        self.holdHorizontal.setChecked(True)
        self.firstRun = True
        self.y0 = None
        self.y1 = None
        self.x0 = None
        self.x1 = None
        self.scanX()
        self.y0 = None
        self.y1 = None
        self.middleX = None
        self.middleY = None
        self.y0 = 500
        self.y1 = 1600

        self.defineRectangle()
        self.drawRectangle()
        self.firstRun = False



    def setRectangleFromEntry(self):
        width = int(self.recWidthEntry.displayText())
        heigth = int(self.recHeigthEntry.displayText())
        self.middleX = int(self.middleXEntry.displayText())
        self.middleY = int(self.middleYEntry.displayText())
        y0 = int(abs((self.y1 + self.y0)) / 2 - heigth/2)
        y1 = int(abs((self.y1 + self.y0)) / 2 + heigth/2)
        self.y0 = y0
        self.y1 = y1
        x0 = int(abs((self.x1 + self.x0)) / 2 - width/2)
        x1 = int(abs((self.x1 + self.x0)) / 2 + width/2)
        self.x0 = x0
        self.x1 = x1
        self.defineRectangle(width=width, heigth=heigth)
        self.drawRectangle()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()

    def defineRectangle(self, y0 = None, y1 = None, x0 = None, x1 = None, width = None, heigth = None):
        if y0 == None:
            y0 = self.y0
        if y1 == None:
            y1 = self.y1
        if x0 == None:
            x0 = self.x0
        if x1 == None:
            x1 = self.x1
        if width == None:
            width = x1 - x0
        if heigth == None:
            heigth = y1 - y0

        if self.middleX == None:
            self.middleX = (x0 + x1)/2
        if self.middleY == None:
            self.middleY = (y0+y1)/2


        self.rect.set_width(width)
        self.rect.set_height(heigth)
        self.rect.set_xy((self.middleX - (width / 2), self.middleY - (heigth / 2)))
        self.recHeigthEntry.setText(str(abs(int(heigth))))
        self.recWidthEntry.setText(str(abs(int(width))))
        self.middleXEntry.setText(str(int(self.middleX)))
        self.middleYEntry.setText(str(int(self.middleY)))


    def drawRectangle(self):
        figure = self.figurecanvas[0]
        ax = figure.axes[0]
        ax.add_patch(self.rect)
        self.figurecanvas[1].draw()

    def on_press(self, event):
        self.clicked = True
        self.x0 = int(event.xdata)
        self.y0 = int(event.ydata)


    def on_hover(self, event):
        if self.clicked == True:
            self.x1 = int(event.xdata)
            self.y1 = int(event.ydata)
            self.middleX = int((self.x0 + self.x1) / 2)
            self.middleY = int((self.y0 + self.y1) / 2)
            self.defineRectangle()
            self.drawRectangle()

    def YonedaScan(self):
        self.y0 = 1370
        self.y1 = 1375
        self.x0 = 369
        self.x1 = 1369
        self.middleY = (self.y0 + self.y1)/2
        self.middleX = (self.x0+self.x1)/2
        self.recHeigthEntry.setText(str(5))
        self.recWidthEntry.setText(str(1000))
        self.middleXEntry.setText(str(int(self.middleX)))
        self.middleYEntry.setText(str(int(self.middleY)))
        self.defineRectangle()
        self.drawRectangle()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()


    def findSpecular(self):
        self.y0 = 1450
        self.y1 = 1500
        self.x0 = 550
        self.x1 = 1200
        self.middleY = (self.y0 + self.y1)/2
        self.middleX = (self.x0+self.x1)/2
        self.defineRectangle()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()
        peakindex = gisax.detectPeak(self, self.intensity_x[0])[0]
        self.middleX = self.intensity_x[1][peakindex]


    def scanX(self):
        self.findSpecular()
        self.y0 = 500
        self.y1 = 1600
        heigth = self.y1 - self.y0
        self.x0 = self.middleX - 5
        self.x1 = self.middleX + 5
        width = self.middleX
        self.defineRectangle(width=width, heigth=heigth)
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()

    def on_release(self, event):
        self.clicked = False
        self.defineRectangle()
        self.drawRectangle()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()


    def calcOffSpec(self):
        if self.holdHorizontal.isChecked() == False:
            self.startHorizontal(hold_horizontal = False)
        else:
            self.startHorizontal(hold_horizontal = True)
        if self.holdVertical.isChecked() == False:
            self.startVertical(hold_vertical = False)
        else:
            self.startVertical(hold_vertical = True)

    def startHorizontal(self, hold_horizontal = False):
        if hold_horizontal == False:
            if self.firstRun == False:
                self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
                self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
                self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
                self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)

            startstop = self.find_startstop()
            startx = startstop[0]
            stopx = startstop[1]
            starty = startstop[2]
            stopy = startstop[3]

            intensity_list = self.calcHorizontal(startx, stopx, starty, stopy)
            coordinatelist = list(range(startx, stopx))
            data = self.removeZeroes(intensity_list, coordinatelist)
            self.intensity_x = data
        else:
            data = self.intensity_x

        layout = self.graphlayout
        self.horizontalscanfig = gisax.plotGraphOnCanvas(self, layout, data[1], data[0], title="Horizontal scan")
        self.horizontalscanfig[1].canvas.mpl_connect('motion_notify_event', lambda event: self.dragVline(event, scan="horizontal"))
        self.horizontalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.horizontalscanfig[1].canvas.mpl_connect('button_release_event', lambda event: self.releaseVline(event, scan="horizontal"))

    def calcHorizontal(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        for i in range(startx, stopx):
            for j in range(starty, stopy):
                intensity += self.data[j][i]
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

    def startVertical(self, hold_vertical = False):
        if hold_vertical == False:
            if self.firstRun == False:
                self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
                self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
                self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
                self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)
            startstop = self.find_startstop()
            startx = startstop[0]
            stopx = startstop[1]
            starty = startstop[2]
            stopy = startstop[3]
            intensity_list = self.calcVertical(startx, stopx, starty, stopy)
            coordinatelist = list(range(min([int(self.y0), int(self.y1)]), max([int(self.y0), int(self.y1)])))
            data = self.removeZeroes(intensity_list, coordinatelist)
            self.intensity_y = data
        else:
            data = self.intensity_y
        layout = self.graphlayout
        self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, data[1], data[0], title="Vertical scan", revert = True)
        self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', lambda event: self.dragVline(event, scan="vertical"))
        self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_release_event', lambda event: self.releaseVline(event, scan="vertical"))

    def calcVertical(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        for i in range(starty, stopy):
            for j in range(startx, stopx):
                intensity += self.data[i][j]
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

    def dragVline(self, event, scan = "vertical"):
        if self.clicked == True and self.dragButton.isChecked():
            if hasattr(self, 'vline'):
                self.vline.remove()

            if scan == "horizontal":
                figure = self.horizontalscanfig[0]
                canvas = self.horizontalscanfig[1]
                self.middleX = event.xdata
            if scan == "vertical":
                figure = self.verticalscanfig[0]
                canvas = self.verticalscanfig[1]
                self.middleY = event.xdata

            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            canvas.draw()
            if self.performanceButton.isChecked():
                pass
            else:
                #self.fitRectange()
                self.defineRectangle()
                self.drawRectangle()


    def pressVline(self, event):
        self.clicked = True

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

    def find_FWHM(self, position, scan="vertical"):
        if scan == "horizontal":
            xdata = self.intensity_x[1]
            ydata = self.intensity_x[0]
            figure = self.horizontalscanfig[0]
            axes = figure.axes[0]
            canvas = self.horizontalscanfig[1]

        if scan == "vertical":
            xdata = self.intensity_y[1]
            ydata = self.intensity_y[0]
            figure = self.verticalscanfig[0]
            axes = figure.axes[0]
            canvas = self.verticalscanfig[1]
        peak_position = self.find_peak_in_range(position, xdata, ydata)


        half_intensity = ydata[peak_position]/2
        #Find left boundary:

        interfunction = interp1d(xdata[::-1], ydata[::-1], kind='linear')
        xs = np.sort(xdata)
        ys = np.array(ydata)[np.argsort(xdata)]
        x0 = 1200
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

    def releaseVline(self, event, scan = ""):
        self.clicked = False

        if scan == "vertical":
            figure = self.verticalscanfig[0]
            canvas = self.verticalscanfig[1]
        if scan == "horizontal":
            figure = self.horizontalscanfig[0]
            canvas = self.horizontalscanfig[1]


        if self.findFWHM_button.isChecked():
            FWHM = self.find_FWHM(event.xdata, scan=scan)
            self.FWHM_entry.setText(str(round(FWHM,2)))

        if self.dragButton.isChecked():
            if hasattr(self, 'vline'):
                self.vline.remove()

            #Will find a more elegant solution to seperate these two cases hesre
            if scan == "vertical":
                self.middleY = event.xdata
            if scan == "horizontal":
                self.middleX = event.xdata
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            canvas.draw()
            self.clearLayout(self.graphlayout)
            self.calcOffSpec()
            self.defineRectangle()
            self.drawRectangle()
            self.figurecanvas[1].draw()


    def saveFileDialog(self, documenttype="Text file (*.txt)"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", self.filename[:-4],
                                               documenttype, options=options)
        return fileName

    def saveFile(self, horizontal = True):
        path = self.saveFileDialog()
        filename = path[0]
        if filename[-4:] != ".txt":
            filename = filename + ".txt"
        if horizontal == True:
            array = np.stack([self.intensity_x[1], self.intensity_x[0]], axis=1)
        else:
            array = np.stack([self.intensity_y[1][::-1], self.intensity_y[0]], axis=1)
        np.savetxt(filename, array, delimiter="\t")




    def plotFigure(self, x, y, title=""):
        plt.figure()
        plt.plot(x, y)
        plt.yscale('log')
        plt.title(title)
        plt.show()



    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


def setUpWindow():
    app = QtWidgets.QApplication(sys.argv)
    nowWindow = CallUI()
    nowWindow.showMaximized()
    sys.exit(app.exec_())

