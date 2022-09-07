#CallUI.py
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import os
import shutil
import platform
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

        config_path = settings.get_path()
        if not os.path.isfile(config_path + "config.json"):
            if platform.system() == "Windows":
                shutil.copy("config.json", config_path + "\config.json")
            else:
                shutil.copy("config.json", config_path + "/config.json")
            print(f"Saved config file in {config_path}")

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
        xmin = middle_x - width / 2
        xmax = middle_x + width / 2
        ymin = middle_y - height / 2
        ymax = middle_y + height / 2
        extents = [xmin, xmax, ymin, ymax]
        # self.ROI_scan_rect.draw_shape(coords)
        self.ROI_scan_rect.extents = extents
        self.clearLayout(self.graphlayout)
        scan.calcOffSpec(self)

    def set_entry(self, height, width, x, y):
        rounding = 3
        self.recHeigthEntry.setText(str(abs(round(float(height), rounding))))
        self.recWidthEntry.setText(str(abs(round(float(width), rounding))))
        self.middleXEntry.setText(str(round(float(x), rounding)))
        self.middleYEntry.setText(str(round(float(y), rounding)))
        extends = [(x - width/2), x + width/2, y-height/2, y + height/2]
        self.ROI_scan_rect.to_draw.set_visible(True)
        self.ROI_scan_rect.extents = extends


    def define_rectangle(self):
        self.ROI_scan_rect = RectangleSelector(self.figurecanvas[0].axes[0], self.on_release,
                                                drawtype='box', useblit=True,
                                                button=[1],  # don't use middle button
                                                minspanx=0.1, minspany=0.1,
                                                spancoords='pixels',
                                                interactive=True)

        self.ROI_background_rect = RectangleSelector(self.figurecanvas[0].axes[0], self.on_release,
                                                drawtype='box', useblit=True,
                                                button=[1],  # don't use middle button
                                                minspanx=0.1, minspany=0.1,
                                                spancoords='pixels',
                                                interactive=True, rectprops=dict(facecolor='yellow', alpha=0.35))
        self.ROI_background_rect.set_active(False)



    def press_bg_ROI_button(self):
        if self.bg_ROI_button.isChecked():
            self.ROI_background_rect.set_visible(True)
            self.ROI_background_rect.set_active(True)
            self.ROI_button.setChecked(False)
            self.ROI_scan_rect.set_visible(False)
            self.ROI_scan_rect.set_active(False)
            self.figurecanvas[1].draw()


        else:
            self.ROI_background_rect.set_visible(False)
            self.ROI_background_rect.set_active(False)
            self.figurecanvas[1].draw()


    def press_ROI_button(self):
        if self.ROI_button.isChecked():
            self.ROI_scan_rect.set_visible(True)
            self.ROI_scan_rect.set_active(True)
            self.bg_ROI_button.setChecked(False)
            self.ROI_background_rect.set_visible(False)
            self.ROI_background_rect.set_active(False)
            self.figurecanvas[1].draw()

        else:
            self.ROI_scan_rect.set_visible(False)
            self.ROI_scan_rect.set_active(False)
            self.figurecanvas[1].draw()



    def on_press(self, event):
        self.clicked = True
        if self.ROI_button.isChecked():
            self.ROI_scan.x0 = float(event.xdata)
            self.ROI_scan.y0 = float(event.ydata)
        if self.bg_ROI_button.isChecked():
            self.ROI_background.x0 = float(event.xdata)
            self.ROI_background.y0 = float(event.ydata)

    def on_release(self, eclick, erelease):
        self.clicked = False
        if self.ROI_button.isChecked():
            width = abs(eclick.xdata - erelease.xdata)
            heigth = abs(eclick.ydata - erelease.ydata)
            self.middleX = (eclick.xdata + erelease.xdata)/2
            self.middleY = (eclick.ydata + erelease.ydata)/2
            rounding = 3

            self.recHeigthEntry.setText(str(abs(round(float(heigth), rounding))))
            self.recWidthEntry.setText(str(abs(round(float(width),rounding))))
            self.middleXEntry.setText(str(round(float(self.middleX),rounding)))
            self.middleYEntry.setText(str(round(float(self.middleY),rounding)))

            self.clearLayout(self.graphlayout)
            scan.calcOffSpec(self)

        if self.bg_ROI_button.isChecked():
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
            xmin, xmax, ymin, ymax = self.ROI_scan_rect.extents
            extents = [xmin, xmax, ymin, ymax]

            middleY = (ymin + ymax)/2
            middleX = (xmin + xmax)/2
            if scan_type == "vertical":
                y_shift = (event.xdata - middleY)
                ymin += y_shift
                ymax += y_shift
                extents = [xmin, xmax, ymin, ymax]
                self.ROI_scan_rect.to_draw.set_visible(True)
                self.ROI_scan_rect.extents = extents
            if scan_type == "horizontal":
                x_shift = (event.xdata - middleX)
                xmin += x_shift
                xmax += x_shift
                extents = [xmin, xmax, ymin, ymax]
                self.ROI_scan_rect.to_draw.set_visible(True)
                self.ROI_scan_rect.extents = extents

 #           coords = [xmin, xmax, ymin, ymax]
#            self.ROI_scan_rect.draw_shape(coords)



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
            xmin, xmax, ymin, ymax = self.ROI_scan_rect.extents
            extents = [xmin, xmax, ymin, ymax]
            middleY = (ymin + ymax)/2
            middleX = (xmin + xmax)/2
            if scan_type == "vertical":
                y_shift = (event.xdata - middleY)
                ymin += y_shift
                ymax += y_shift
            if scan_type == "horizontal":
                x_shift = (event.xdata - middleX)
                xmin += x_shift
                xmax += x_shift
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            canvas.draw()
            self.clearLayout(self.graphlayout)
            scan.calcOffSpec(self)


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

