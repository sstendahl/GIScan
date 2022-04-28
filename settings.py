import CallUI
import json
import sys
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem

import gisaxs


def openSettingsdialog(self):
    self.settingsdialog = CallUI.settingsUI()
    with open('config.json', 'r') as f:
        config = json.load(f)
    cmaps = [('Perceptually Uniform Sequential', [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
             ('Sequential', [
                 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
             ('Sequential (2)', [
                 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                 'hot', 'afmhot', 'gist_heat', 'copper']),
             ('Diverging', [
                 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
             ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
             ('Qualitative', [
                 'Pastel1', 'Pastel2', 'Paired', 'Accent',
                 'Dark2', 'Set1', 'Set2', 'Set3',
                 'tab10', 'tab20', 'tab20b', 'tab20c']),
             ('Miscellaneous', [
                 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                 'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                 'gist_ncar'])]




    for cmap_category, cmap_list in cmaps:
        self.settingsdialog.cmap_category_widget.addItem(cmap_category)

    self.settingsdialog.cmap_category_widget.activated.connect(lambda: populate_cmaplist(self, config, cmaps))
    select_current_cmap(self, cmaps, config)
    populate_cmaplist(self, config, cmaps)
    select_current_cmap(self, cmaps, config)
    self.settingsdialog.show()
    self.settingsdialog.accepted.connect(lambda: writeConfig(self))

def select_current_cmap(self, cmaps, config):
    current_cat = config["cmap_cat"]
    current_cmap = config["cmap"]

    for index, category in enumerate(cmaps):
        if category[0] == current_cat:
            cat_index = index
            index = 0
            for cmap in category[1]:
                if cmap == current_cmap:
                    cmap_index = index
                index += 1
                if f"{cmap}_r" == current_cmap:
                    cmap_index = index
                index += 1


    self.settingsdialog.cmap_category_widget.setCurrentIndex(cat_index)
    self.settingsdialog.cmap_list_widget.setCurrentIndex(cmap_index)

def populate_cmaplist(self, config, cmaps):
    index = 0
    cmapindex = 0
    current_index = self.settingsdialog.cmap_category_widget.currentIndex()
    self.settingsdialog.cmap_list_widget.clear()
    current_cmap = config["cmap"]
    for map in cmaps[current_index][1]:
        self.settingsdialog.cmap_list_widget.addItem(map)
        if map == current_cmap:
            cmapindex = index
        self.settingsdialog.cmap_list_widget.addItem(f"{map}_r")
        index += 1
        if f"{map}_r" == current_cmap:
            cmapindex = index
        index += 1



def get_cmap():
    os.chdir(sys.path[0])
    with open('config.json', 'r') as f:
        config = json.load(f)
    cmap = config["cmap"]
    return cmap

def writeConfig(self):
    with open('config.json', 'r') as f:
        config = json.load(f)

    cmap = str(self.settingsdialog.cmap_list_widget.currentText())
    config["cmap"] = cmap
    cmap_cat = str(self.settingsdialog.cmap_category_widget.currentText())
    config["cmap_cat"] = cmap_cat

    with open('config.json', 'w') as f:
        json.dump(config, f)
    print(self.sampledata.path)
    gisaxs.loadMap(self, self.sampledata.path)

def showAbout(self):
    self.aboutWindow = CallUI.aboutWindow()
    self.aboutWindow.show()

