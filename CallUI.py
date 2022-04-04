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
        print(self.x0)

    def on_hover(self, event):
        if self.clicked == True:
            self.x1 = int(event.xdata)
            self.y1 = int(event.ydata)
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            figure = self.figurecanvas[0]
            print(figure.axes[0])
            ax = 0
            ax = figure.axes[0]
            try:
                ax.patches = []
            except:
                pass
            print(self.rect)
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
        ax.patches = []



    def calcOffSpec(self):
        print(f"The x-coordinates span from x0={self.x0} to x1={self.x1}")
        print(f"The y-coordinates span from y0={self.y0} to y10={self.y1}")

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
        print(f"Starty is equal to {starty}")
        print(f"stopy is equal to {stopy}")

        intensity_list = self.calcHorizontal(startx, stopx, starty, stopy)
        intensity_list = self.removeZeroes(intensity_list)
        self.intensity_x = intensity_list
        layout = self.graphlayout
        gisax.plotGraphOnCanvas(self, layout, intensity_list[1], intensity_list[0], title="Horizontal scan")

        intensity_list = self.calcVertical(startx, stopx, starty, stopy)
        intensity_list = self.removeZeroes(intensity_list)
        self.intensity_y = intensity_list
        gisax.plotGraphOnCanvas(self, layout, intensity_list[1][::-1], intensity_list[0], title="Vertical scan")

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

    def removeZeroes(self, intensity_list):
        new_list = []
        indexlist = []
        for index in range(len(intensity_list)):
            if intensity_list[index] > 0:
                new_list.append(intensity_list[index])
                indexlist.append(index)
        print(min(new_list))
        return [new_list, indexlist]


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

