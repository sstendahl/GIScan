# CallUI.py
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import os
import shutil
import fwhmscan
import settings
import gisaxs
from PyQt5 import QtGui
import scanning_tools as scan

Ui_MainWindow, QtBaseClass = uic.loadUiType("form.ui")
Ui_settingsDialog, settingsDialogClass = uic.loadUiType("settingsdialog.ui")
Ui_fwhmscan_window, fwhmscan_windowClass = uic.loadUiType("fwhmscan_window.ui")
Ui_fwhmscan_result_window, fwhmscan_result_windowClass = uic.loadUiType("fwhmscan_result_window.ui")

class fwhmscanUI(fwhmscan_windowClass, Ui_fwhmscan_window):
    def __init__(self, parent=None):
        fwhmscan_windowClass.__init__(self, parent)
        self.setupUi(self)

class fwhmscan_resultUI(fwhmscan_result_windowClass, Ui_fwhmscan_result_window):
    def __init__(self, parent=None):
        fwhmscan_result_windowClass.__init__(self, parent)
        self.setupUi(self)


class settingsUI(settingsDialogClass, Ui_settingsDialog):
    def __init__(self, parent=None):
        settingsDialogClass.__init__(self, parent)
        self.setupUi(self)


class CallUI(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setWindowIcon\
            (QtGui.QIcon('logo.png'))
        self.setupUi(self)
        self.sampledata = None
        self.clicked = False
        self.ROI_scan_rect = None
        self.ROI_background_rect = None
        config_path = settings.get_path()
        if not os.path.isfile(f"{config_path}/config.json"):
            if not os.path.isdir(config_path):
                os.mkdir(config_path)
            path = config_path + "/config.json"
            shutil.copy("config.json", path)
            print(f"Saved config file in {config_path}")
        
        gisaxs.loadEmpty(self)
        self.connectActions()
     
    def loadMap(self):
        path = scan.getPath()
        gisaxs.loadMap(path)

    def connectActions(self):
        # Connect File actions
        self.load_button.clicked.connect(lambda: gisaxs.loadMap_from_file_picker(self))
        self.settings_button.clicked.connect(lambda: settings.openSettingsdialog(self))
        if self.sampledata is not None:
            self.saveVertical.clicked.connect(lambda: self.saveFile(horizontal=False))
            self.saveHorizontal.clicked.connect(lambda: self.saveFile(horizontal=True))
            self.setRec.clicked.connect(lambda: self.setRectangleFromEntry())
            self.yoneda_button.clicked.connect(lambda: scan.YonedaScan(self))
            self.detector_button.clicked.connect(lambda: scan.detector_scan(self))
            self.dragButton.clicked.connect(self.press_drag_button)
            self.fwhmscan_button.clicked.connect(lambda: fwhmscan.open_fwhmscan_window(self))
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
        self.ROI_scan_rect.extents = extents
        self.clearLayout(self.horizontal_layout)
        self.clearLayout(self.vertical_layout)
        scan.calcOffSpec(self)



    def set_entry(self, height, width, x, y):
        rounding = 4
        self.recHeigthEntry.setText(str(abs(round(float(height), rounding))))
        self.recWidthEntry.setText(str(abs(round(float(width), rounding))))
        self.middleXEntry.setText(str(round(float(x), rounding)))
        self.middleYEntry.setText(str(round(float(y), rounding)))
        extends = [(x - width / 2), x + width / 2, y - height / 2, y + height / 2]
        self.ROI_scan_rect.to_draw.set_visible(True)
        self.ROI_scan_rect.extents = extends

    def define_rectangle(self):
        self.ROI_scan_rect = RectangleSelector(self.figurecanvas[0].axes[0], self.on_release,
                                               drawtype='box', useblit=True,
                                               button=[1],  # don't use middle button
                                               minspanx=0.1, minspany=0.1,
                                               spancoords='pixels',
                                               interactive=True,
                                               rectprops=dict(linestyle='-', color='red', alpha=0.2, linewidth=2))

        self.ROI_background_rect = RectangleSelector(self.figurecanvas[0].axes[0], self.on_release,
                                                     drawtype='box', useblit=True,
                                                     button=[1],  # don't use middle button
                                                     minspanx=0.1, minspany=0.1,
                                                     spancoords='pixels',
                                                     interactive=True,
                                                     rectprops=dict(linestyle='-', color='yellow', alpha=0.2,
                                                                    linewidth=2))
        self.ROI_background_rect.extents = [0, 0, 0, 0]
        self.ROI_background_rect.set_visible(False)
        self.ROI_background_rect.set_active(False)

    def press_bg_ROI_button(self):
        if self.ROI_scan_rect is not None:
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
        if self.ROI_scan_rect is not None:
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
        if self.bg_ROI_button.isChecked():
            self.sampledata.average_bg = scan.get_average_background(self)
            self.clearLayout(self.horizontal_layout)
            self.clearLayout(self.vertical_layout)
            scan.calcOffSpec(self)

        if self.ROI_button.isChecked():
            width = abs(eclick.xdata - erelease.xdata)
            heigth = abs(eclick.ydata - erelease.ydata)
            middleX = (eclick.xdata + erelease.xdata) / 2
            middleY = (eclick.ydata + erelease.ydata) / 2
            rounding = 4

            self.recHeigthEntry.setText(str(abs(round(float(heigth), rounding))))
            self.recWidthEntry.setText(str(abs(round(float(width), rounding))))
            self.middleXEntry.setText(str(round(float(middleX), rounding)))
            self.middleYEntry.setText(str(round(float(middleY), rounding)))

            self.clearLayout(self.horizontal_layout)
            self.clearLayout(self.vertical_layout)
            scan.calcOffSpec(self)

    def dragVline(self, event, scan_type="vertical"):
        if self.clicked == True and self.dragButton.isChecked() and self.ROI_button.isChecked():

            # Remove old vertical line
            if hasattr(self, 'vline'):
                try:
                    self.vline.remove()
                except:
                    print("Couldn't remove vline")

            if scan_type == "horizontal":
                figure = self.horizontalscanfig[0]
                canvas = self.horizontalscanfig[1]
            if scan_type == "vertical":
                figure = self.verticalscanfig[0]
                canvas = self.verticalscanfig[1]

            # Draw vertical line
            axle = figure.axes[0]
            self.vline = (axle.axvline(event.xdata, color='k', linewidth=1.0,
                                       linestyle='--'))  # Change the line in the list to new selected line
            canvas.draw()

            # Move ROI
            xmin, xmax, ymin, ymax = self.ROI_scan_rect.extents
            middleY = (ymin + ymax) / 2
            middleX = (xmin + xmax) / 2
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

    def pressVline(self, event):
        self.clicked = True

    def releaseVline(self, event, scan_type=""):
        self.clicked = False

        if self.findFWHM_button.isChecked():
            FWHM = scan.find_FWHM(self, event.xdata, scan_type=scan_type)
            self.FWHM_entry.setText(str(round(FWHM, 6)))

        if hasattr(self, 'vline'):
            try:
                self.vline.remove()
            except:
                print("Couldn't remove vline")

        if self.dragButton.isChecked() and self.ROI_button.isChecked():
            x0, x1, y0, y1 = self.ROI_scan_rect.extents
            height = y1 - y0
            width = x1 - x0
            middleY = (y0 + y1) / 2
            middleX = (x0 + x1) / 2
            self.set_entry(height, width, middleX, middleY)
            if scan_type == "horizontal" and self.holdHorizontal.isChecked():
                self.clearLayout(self.vertical_layout)
                scan.calcOffSpec(self, scan = "vertical")
            if scan_type == "vertical" and self.holdVertical.isChecked():
                self.clearLayout(self.horizontal_layout)
                scan.calcOffSpec(self, scan = "horizontal")
            else:
                self.clearLayout(self.horizontal_layout)
                self.clearLayout(self.vertical_layout)
                scan.calcOffSpec(self, scan = "both")


    def saveFileDialog(self, filename = None, documenttype="Text file (*.txt)", title="Save file"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        if filename == None:
            filename = self.filename[:-4]
        fileName = QFileDialog.getSaveFileName(self, title, filename,
                                               documenttype, options=options)
        return fileName

    def saveFile(self, horizontal=True):
        if horizontal:
            path = self.saveFileDialog(title="Save horizontal scan")
        elif not horizontal:
            path = self.saveFileDialog(title="Save vertical scan")
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
