#CallUI.py
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import settings
import gisaxs
from PyQt5 import QtGui
import scanning_tools as scan
Ui_MainWindow, QtBaseClass = uic.loadUiType("form.ui")
Ui_settingsDialog, settingsDialogClass = uic.loadUiType("settingsdialog.ui")


class settingsUI(settingsDialogClass, Ui_settingsDialog):
    def __init__(self, parent=None):
        settingsDialogClass.__init__(self, parent)
        self.setupUi(self)


class CallUI(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setupUi(self)
        self.connectActions()
        self.sampledata = None
        self.clicked = False
        self.middleX = None
        self.middleY = None
        gisaxs.loadEmpty(self)

    def loadMap(self):
        path = scan.getPath()
        gisaxs.loadMap(path)

    def connectActions(self):
        # Connect File actions
        self.load_button.clicked.connect(lambda: gisaxs.loadMap_from_file_picker(self))
        self.saveVertical.clicked.connect(lambda: self.saveFile(horizontal=False))
        self.saveHorizontal.clicked.connect(lambda: self.saveFile(horizontal=True))
        self.setRec.clicked.connect(lambda: self.setRectangleFromEntry())
        self.yoneda_button.clicked.connect(lambda: scan.YonedaScan(self))
        self.detector_button.clicked.connect(lambda: scan.detector_scan(self))
        self.dragButton.clicked.connect(self.press_drag_button)
        self.settings_button.clicked.connect(lambda: settings.openSettingsdialog(self))
        self.findFWHM_button.clicked.connect(self.press_FWHM_button)
        self.ROI_button.clicked.connect(self.press_ROI_button)
        self.bg_ROI_button.clicked.connect(self.press_bg_ROI_button)


    def press_drag_button(self):
        if self.dragButton.isChecked():
            self.findFWHM_button.setChecked(False)


    def press_FWHM_button(self):
        if self.findFWHM_button.isChecked():
            self.dragButton.setChecked(False)


    def setRectangleFromEntry(self):
        width = float(self.recWidthEntry.displayText())
        height = float(self.recHeigthEntry.displayText())

        middle_x = float(self.middleXEntry.displayText())
        middle_y = float(self.middleYEntry.displayText())
        self.ROI_scan.x0 = middle_x - width / 2
        self.ROI_scan.x1 = middle_x + width / 2
        self.ROI_scan.y0 = middle_y - height / 2
        self.ROI_scan.y1 = middle_y + height / 2



        self.middleX = float(self.middleXEntry.displayText())
        self.middleY = float(self.middleYEntry.displayText())
        self.defineRectangle(width=width, heigth=height)
        self.drawRectangle()
        self.clearLayout(self.graphlayout)
        scan.calcOffSpec(self)

    def defineRectangle(self, y0 = None, y1 = None, x0 = None, x1 = None, width = None, heigth = None, type = "scan"):
        if type == "scan":
            ROI = self.ROI_scan
        else:
            ROI = self.ROI_background
        if y0 == None:
            y0 = ROI.y0
        if y1 == None:
            y1 = ROI.y1
        if x0 == None:
            x0 = ROI.x0
        if x1 == None:
            x1 = ROI.x1
        if width == None:
            width = x1 - x0
        if heigth == None:
            heigth = y1 - y0

        if self.middleX == None:
            self.middleX = (x0 + x1)/2
        if self.middleY == None:
            self.middleY = (y0+y1)/2


        if settings.get_config("mapping") == "q-space":
            rounding = 4
        else:
            rounding = 2

        if type == "scan":
            self.recHeigthEntry.setText(str(abs(round(float(heigth), rounding))))
            self.recWidthEntry.setText(str(abs(round(float(width),rounding))))
            self.middleXEntry.setText(str(round(float(self.middleX),rounding)))
            self.middleYEntry.setText(str(round(float(self.middleY),rounding)))

        ROI.x0 = self.middleX - width / 2
        ROI.x1 = self.middleX + width / 2
        ROI.y0 = self.middleY - heigth / 2
        ROI.y1 = self.middleY + heigth / 2

        ROI.set_width(width)
        ROI.set_height(heigth)
        ROI.set_xy((self.middleX - (width / 2), self.middleY - (heigth / 2)))


    def drawRectangle(self):
        figure = self.figurecanvas[0]
        figure.canvas.restore_region(self.background)
        ax = figure.axes[0]
        figure.canvas.blit(ax.bbox)
        self.figurecanvas[1].draw()


    def press_bg_ROI_button(self):
        if self.bg_ROI_button.isChecked():
            self.ROI_background.set_visible(True)
            self.ROI_button.setChecked(False)
            self.ROI_scan.set_visible(False)

        else:
            self.ROI_background.set_visible(False)
        self.drawRectangle()

    def press_ROI_button(self):
        if self.ROI_button.isChecked():
            self.ROI_scan.set_visible(True)
            self.bg_ROI_button.setChecked(False)
            self.ROI_background.set_visible(False)
        else:
            self.ROI_scan.set_visible(False)
        self.drawRectangle()



    def on_press(self, event):
        self.clicked = True
        if self.ROI_button.isChecked():
            self.ROI_scan.x0 = float(event.xdata)
            self.ROI_scan.y0 = float(event.ydata)
        if self.bg_ROI_button.isChecked():
            self.ROI_background.x0 = float(event.xdata)
            self.ROI_background.y0 = float(event.ydata)



    def on_hover(self, event):
        if self.clicked and self.ROI_button.isChecked():
            self.ROI_scan.x1 = float(event.xdata)
            self.ROI_scan.y1 = float(event.ydata)
            self.middleX = float((self.ROI_scan.x0 + self.ROI_scan.x1) / 2)
            self.middleY = float((self.ROI_scan.y0 + self.ROI_scan.y1) / 2)
            self.defineRectangle()
            self.drawRectangle()
        if self.clicked and self.bg_ROI_button.isChecked():
            self.ROI_background.x1 = float(event.xdata)
            self.ROI_background.y1 = float(event.ydata)
            self.middleX = float((self.ROI_background.x0 + self.ROI_background.x1) / 2)
            self.middleY = float((self.ROI_background.y0 + self.ROI_background.y1) / 2)

            self.defineRectangle(type="bg")
            self.drawRectangle()



    def on_release(self, event):
        self.clicked = False
        if self.ROI_button.isChecked():
            self.defineRectangle()
            self.drawRectangle()
            self.clearLayout(self.graphlayout)
            scan.calcOffSpec(self)

        if self.bg_ROI_button.isChecked():
            self.defineRectangle(type="bg")
            self.drawRectangle()
            self.sampledata.average_bg = scan.get_average_background(self)



    def dragVline(self, event, scan_type = "vertical"):
        if self.clicked == True and self.dragButton.isChecked():
            if hasattr(self, 'vline'):
                self.vline.remove()

            if scan_type == "horizontal":
                figure = self.horizontalscanfig[0]
                canvas = self.horizontalscanfig[1]
                self.middleX = event.xdata
            if scan_type == "vertical":
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


    def releaseVline(self, event, scan_type = ""):
        self.clicked = False

        if scan_type == "vertical":
            figure = self.verticalscanfig[0]
            canvas = self.verticalscanfig[1]
        if scan_type == "horizontal":
            figure = self.horizontalscanfig[0]
            canvas = self.horizontalscanfig[1]


        if self.findFWHM_button.isChecked():
            FWHM = scan.find_FWHM(self, event.xdata, scan_type=scan_type)
            self.FWHM_entry.setText(str(round(FWHM,6)))

        if self.dragButton.isChecked():
            if hasattr(self, 'vline'):
                self.vline.remove()

            #Will find a more elegant solution to seperate these two cases hesre
            if scan_type == "vertical":
                self.middleY = event.xdata
            if scan_type == "horizontal":
                self.middleX = event.xdata
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            canvas.draw()
            self.clearLayout(self.graphlayout)
            scan.calcOffSpec(self)
            self.defineRectangle()
            self.drawRectangle()
            self.figurecanvas[1].draw()


    def saveFileDialog(self, documenttype="Text file (*.txt)", title = "Save file"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getSaveFileName(self, title, self.filename[:-4],
                                               documenttype, options=options)
        return fileName

    def saveFile(self, horizontal = True):
        if horizontal:
            path = self.saveFileDialog(title = "Save horizontal scan")
        elif not horizontal:
            path = self.saveFileDialog(title = "Save vertical scan")
        filename = path[0]
        if filename[-4:] != ".txt":
            filename = filename + ".txt"
        if horizontal == True:
            array = np.stack([self.sampledata.horizontal_scan_x, self.sampledata.horizontal_scan_y], axis=1)
        else:
            array = np.stack([self.sampledata.vertical_scan_x, self.sampledata.vertical_scan_y], axis=1)
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

