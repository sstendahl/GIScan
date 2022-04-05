#CallUI.py
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
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
        self.setRec.clicked.connect(lambda: self.setRectangleFromEntry())

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

        self.fitRectange()
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



    def on_release(self, event):
        self.clicked = False
        self.defineRectangle()
        self.drawRectangle()
        self.clearLayout(self.graphlayout)
        self.calcOffSpec()



    def calcOffSpec(self):
        if self.holdHorizontal.isChecked() == False:
            self.startHorizontal()
        else:
            self.useoldHorizontal()
        if self.holdVertical.isChecked() == False:
            self.startVertical()
        else:
            self.useoldVertical()

    def useoldVertical(self):
        layout = self.graphlayout
        self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, self.intensity_y[1], self.intensity_y[0], title="Vertical scan")
        self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVlineY)
        self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)

    def useoldHorizontal(self):
        layout = self.graphlayout
        self.horizontalscanfig = gisax.plotGraphOnCanvas(self, layout, self.intensity_x[1], self.intensity_x[0], title="Horizontal scan")
        self.horizontalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVlineX)
        self.horizontalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.horizontalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)




    def startHorizontal(self):
        self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
        self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
        self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
        self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)

        start = int(self.x0)
        stop = int(self.x1)
        startx = min([start, stop])
        stopx = max([start, stop])
        start = int(max(self.ylist) - self.y1)
        stop = int(max(self.ylist) - self.y0)
        starty = min([start, stop])
        stopy = max([start, stop])
        intensity_list = self.calcHorizontal(startx, stopx, starty, stopy)
        coordinatelist = list(range(startx, stopx))
        data = self.removeZeroes(intensity_list, coordinatelist)
        self.intensity_x = data

        layout = self.graphlayout
        self.horizontalscanfig = gisax.plotGraphOnCanvas(self, layout, data[1], data[0], title="Horizontal scan")
        self.horizontalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVlineX)
        self.horizontalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.horizontalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)

    def calcHorizontal(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        for i in range(startx, stopx):
            for j in range(starty, stopy):
                intensity += self.z[j][i]
            intensity_list.append(intensity)
            intensity = 0
        return intensity_list

    def startVertical(self):
        self.x0 = int(self.middleX - int(self.recWidthEntry.displayText())/2)
        self.y0 = int(self.middleY - int(self.recHeigthEntry.displayText())/2)
        self.x1 = int(self.middleX + int(self.recWidthEntry.displayText())/2)
        self.y1 = int(self.middleY + int(self.recHeigthEntry.displayText())/2)

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
        coordinatelist = list(range(min([int(self.y0), int(self.y1)]), max([int(self.y0), int(self.y1)])))[::-1]
        data = self.removeZeroes(intensity_list, coordinatelist)
        self.intensity_y = data
        self.verticalscanfig = gisax.plotGraphOnCanvas(self, layout, data[1], data[0], title="Vertical scan")
        self.verticalscanfig[1].canvas.mpl_connect('motion_notify_event', self.dragVlineY)
        self.verticalscanfig[1].canvas.mpl_connect('button_press_event', self.pressVline)
        self.verticalscanfig[1].canvas.mpl_connect('button_release_event', self.releaseVline)

    def calcVertical(self, startx, stopx, starty, stopy):
        intensity = 0
        intensity_list = []
        for i in range(starty, stopy):
            for j in range(startx, stopx):
                intensity += self.z[i][j]
            intensity_list.append(intensity)
            intensity = 0
        return intensity_list


    def removeZeroes(self, intensity_list, coordinatelist):
        new_list = []
        new_coordinatelist = []
        for index in range(len(intensity_list)):
            if intensity_list[index] > 10:
                new_list.append(intensity_list[index])
                new_coordinatelist.append(coordinatelist[index])
        return [new_list, new_coordinatelist]

    def dragVlineX(self, event):
        if self.clicked == True and self.dragButton.isChecked():
            try:
                self.vline.remove()
            except:
                pass
            figure = self.horizontalscanfig[0]
            self.middleX = event.xdata
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            self.defineRectangle()
            self.horizontalscanfig[1].draw()
            if self.performanceButton.isChecked():
                pass
            else:
                self.drawRectangle()


    def dragVlineY(self, event):
        if self.clicked == True and self.dragButton.isChecked():
            try:
                self.vline.remove()
            except:
                pass
            figure = self.verticalscanfig[0]
            self.middleY = event.xdata
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            self.fitRectange()
            self.defineRectangle()
            self.verticalscanfig[1].draw()
            if self.performanceButton.isChecked():
                pass
            else:
                self.drawRectangle()

    def pressVline(self, event):
        self.clicked = True

    def releaseVline(self, event):
        self.clicked = False
        if self.dragButton.isChecked():
            self.clearLayout(self.graphlayout)
            self.calcOffSpec()
            if self.performanceButton.isChecked():
                self.drawRectangle()
            else:
                pass

    def fitRectange(self):
        if self.y0 < 0:
            self.y0 = 0
        if self.y1 < 0:
            self.y1 = 0
        if self.y0 > max(self.ylist):
            self.y0 = max(self.ylist)
        if self.y1 > max(self.ylist):
            self.y1 = max(self.ylist)


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

