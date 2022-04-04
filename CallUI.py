#CallUI.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import gisax

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
        self.x1 = None
        self.y1 = None
        gisax.loadEmpty(self)


    def connectActions(self):
        # Connect File actions
        self.load_button.clicked.connect(lambda: gisax.loadMap(self))
        self.saveVertical.clicked.connect(lambda: self.saveFile(horizontal=False))
        self.saveHorizontal.clicked.connect(lambda: self.saveFile(horizontal=True))


    def on_press(self, event):
        self.clicked = True
        self.x0 = int(event.xdata)
        self.y0 = int(event.ydata)

    def on_hover(self, event):
        if self.clicked == True:
            self.x1 = int(event.xdata)
            self.y1 = int(event.ydata)
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            figure = self.figurecanvas[0]
            ax = figure.axes[0]
            try:
                ax.patches = []
            except:
                pass
            ax.add_patch(self.rect)
            self.figurecanvas[1].draw()



    def on_release(self, event):
        endCoordinates = event
        self.clicked = False
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        figure = self.figurecanvas[0]
        ax = figure.axes[0]
        ax.add_patch(self.rect)
        self.figurecanvas[1].draw()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()



    def calcOffSpec(self):
        print(f"The x-coordinates span from x0={self.x0} to x1={self.x1}")
        print(f"The y-coordinates span from y0={self.y0} to y10={self.y1}")
        self.startHorizontal()
        print(self.holdVertical.isChecked())
        if self.holdVertical.isChecked() == False:
            self.startVertical()
        else:
            self.useoldVertical()

    def useoldVertical(self):
        layout = self.graphlayout
        self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, self.intensity_y[1][::-1], self.intensity_y[0], title="Vertical scan")
        self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)



    def startHorizontal(self):
        start = int(self.x0)
        stop = int(self.x1)
        startx = min([start, stop])
        stopx = max([start, stop])
        start = int(max(self.ylist) - self.y1)
        print(max(self.ylist))
        print(max(self.xlist))
        stop = int(max(self.ylist) - self.y0)
        starty = min([start, stop])
        stopy = max([start, stop])
        intensity_list = self.calcHorizontal(startx, stopx, starty, stopy)
        coordinatelist = list(range(startx, stopx))
        self.intensity_x = self.removeZeroes(intensity_list, coordinatelist)

        layout = self.graphlayout
        self.horizontalscanfig = gisax.plotGraphOnCanvas(self, layout, self.intensity_x[1], self.intensity_x[0], title="Horizontal scan")

    def startVertical(self):
        start = int(self.x0)
        stop = int(self.x1)
        startx = min([start, stop])
        stopx = max([start, stop])
        start = int(max(self.ylist) - self.y1)
        stop = int(max(self.ylist) - self.y0)
        starty = min([start, stop])
        stopy = max([start, stop])
        layout = self.graphlayout
        intensity_list = self.calcVertical(startx, stopx, starty, stopy)
        coordinatelist = list(range(min([int(self.y0), int(self.y1)]), max([int(self.y0), int(self.y1)])))
        self.intensity_y = self.removeZeroes(intensity_list, coordinatelist)

        self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, self.intensity_y[1][::-1], self.intensity_y[0], title="Vertical scan")
        self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)




    def dragVline(self, event):
        print(self.clicked)
        if self.clicked == True:
            try:
                self.vline.remove()
            except:
                pass
            figure = self.verticalscanfig[0]
            axle = figure.axes[0]
            self.vlinepos = event.xdata
            y0 = (event.xdata) - abs((self.y1 - self.y0))/2
            y1 = (event.xdata) + abs((self.y1 - self.y0))/2
            print(y0)
            print(y1)
            self.y1 = y1
            self.y0 = y0
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(y1 - y0)
            self.rect.set_xy((self.x0, y0))
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            self.verticalscanfig[1].draw()
            self.figurecanvas[1].draw()

    def pressVline(self, event):
        self.clicked = True

    def releaseVline(self, event, trigger=False):
        self.clicked = False
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()


    def saveFileDialog(self, documenttype="Portable Document Format (PDF) (*.pdf)"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                               documenttype, options=options)
        return fileName

    def saveFile(self, horizontal = True):
        path = self.saveFileDialog(documenttype="Text file (*.txt)")
        filename = path[0]
        if filename[-4:] != ".txt":
            filename = filename + ".txt"
        if horizontal == True:
            array = np.stack([self.intensity_x[1], self.intensity_x[0]], axis=1)
        else:
            array = np.stack([self.intensity_y[1][::-1], self.intensity_y[0]], axis=1)
        np.savetxt(filename, array, delimiter="\t")



    def calcHorizontal(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        for i in range(startx, stopx):
            for j in range(starty, stopy):
                intensity += self.z[j][i]
            intensity_list.append(intensity)
            intensity = 0
        return intensity_list

    def calcVertical(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        print(f"{starty} is starty")
        print(stopy)
        print(self.y0)
        print(self.y1)
        for i in range(starty, stopy):
            for j in range(startx, stopx):
                intensity += self.z[i][j]
            intensity_list.append(intensity)
            intensity = 0
        return intensity_list

    def plotFigure(self, x, y, title=""):
        plt.figure()
        plt.plot(x, y)
        plt.yscale('log')
        plt.title(title)
        plt.show()

    def removeZeroes(self, intensity_list, coordinatelist):
        new_list = []
        indexlist = []
        new_coordinatelist = []
        for index in range(len(intensity_list)):
            if intensity_list[index] > 2:
                new_list.append(intensity_list[index])
                new_coordinatelist.append(coordinatelist[index])
            else:
                new_list.append(np.nan)
        return [new_list, coordinatelist]


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

