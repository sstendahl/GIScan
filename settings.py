import CallUI
import json
import scanning_tools as scan
import os
import shutil
import gisaxs
from pathlib import Path
import platform

def get_path() -> str:
    if platform.system() == "Windows":
        return os.path.join(os.getenv("appdata"), "GIScan")
    elif platform.system() == "Darwin":
        return os.path.join(str(Path.home()), "Library", "Application Support", "GIScan")
    else:
        if os.getenv("XDG_DATA_HOME"):
            return os.path.join(os.getenv("XDG_DATA_HOME"), "GIScan")
        else:
            return os.path.join(str(Path.home()), ".local", "share", "GIScan")


def openSettingsdialog(self):
    """Opens settings dialog."""
    self.settingsdialog = CallUI.settingsUI()
    config_path = get_path()
    os.chdir(config_path)

    with open("config.json", 'r') as f:
        config = json.load(f)
    load_cmaplist(self)
    self.settingsdialog.ai_line.setText(str(config["ai"]))
    self.settingsdialog.wavelength_line.setText(str(config["wavelength"]))
    self.settingsdialog.sdd_line.setText(str(config["sdd"]))
    self.settingsdialog.dbx_line.setText(str(config["db_x"]))
    self.settingsdialog.dby_line.setText(str(config["db_y"]))
    self.settingsdialog.ps_x_line.setText(str(config["ps_x"]))
    self.settingsdialog.ps_y_line.setText(str(config["ps_y"]))
    self.settingsdialog.dark_graphs.setChecked(config["dark_graphs"])
    check_cbar = config["colorbar"]
    self.settingsdialog.cbar_check.setChecked(check_cbar)
    self.settingsdialog.show()
    self.settingsdialog.accepted.connect(lambda: write_config(self))


def set_experimental_parameters(self):
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)
    config["ai"] = float(self.settingsdialog.ai_line.displayText())
    config["wavelength"] = float(self.settingsdialog.wavelength_line.displayText())
    config["sdd"] = float(self.settingsdialog.sdd_line.displayText())
    config["db_x"] = float(self.settingsdialog.dbx_line.displayText())
    config["db_y"] = float(self.settingsdialog.dby_line.displayText())
    config["ps_x"] = float(self.settingsdialog.ps_x_line.displayText())
    config["ps_y"] = float(self.settingsdialog.ps_y_line.displayText())
    config["mapping"] = str(self.settingsdialog.mapping_widget.currentText())
    config["cbar_pos"] = str(self.settingsdialog.cbar_pos_widget.currentText())
    config["dark_graphs"] = self.settingsdialog.dark_graphs.isChecked()
    if self.settingsdialog.cbar_check.isChecked():
        cbar = 1
    else:
        cbar = 0
    config["colorbar"] = cbar
    try:
        self.sampledata.mapping = config["mapping"]
    except:
        print("No sample loaded yet")
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'w') as f:
        json.dump(config, f)


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

def load_cmaplist(self):
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
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

    for index in range(self.settingsdialog.mapping_widget.count()):
        item = self.settingsdialog.mapping_widget.itemText(index)
        if item == config["mapping"]:
            self.settingsdialog.mapping_widget.setCurrentIndex(index)

    for index in range(self.settingsdialog.cbar_pos_widget.count()):
        item = self.settingsdialog.cbar_pos_widget.itemText(index)
        if item == config["cbar_pos"]:
            self.settingsdialog.cbar_pos_widget.setCurrentIndex(index)

    self.settingsdialog.cmap_category_widget.activated.connect(lambda: populate_cmaplist(self, config, cmaps))
    select_current_cmap(self, cmaps, config)
    populate_cmaplist(self, config, cmaps)
    select_current_cmap(self, cmaps, config)

def populate_cmaplist(self, config, cmaps):
    current_index = self.settingsdialog.cmap_category_widget.currentIndex()
    self.settingsdialog.cmap_list_widget.clear()
    for map in cmaps[current_index][1]:
        self.settingsdialog.cmap_list_widget.addItem(map)
        self.settingsdialog.cmap_list_widget.addItem(f"{map}_r")


def write_config(self):
    set_experimental_parameters(self)
    set_cmap(self)
    if self.ROI_scan_rect is not None:
        gisaxs.loadMap(self, self.sampledata.path)
        scan.detector_scan(self)
        self.holdHorizontal.setChecked(False)
        scan.YonedaScan(self)


def get_config(key):
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)
    try:
        item = config[key]
    except KeyError:
        item = None
    return item


def get_cmap():
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)
    cmap = config["cmap"]
    return cmap


def set_cmap(self):
    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'r') as f:
        config = json.load(f)

    cmap = str(self.settingsdialog.cmap_list_widget.currentText())
    config["cmap"] = cmap
    cmap_cat = str(self.settingsdialog.cmap_category_widget.currentText())
    config["cmap_cat"] = cmap_cat

    config_path = get_path()
    os.chdir(config_path)
    with open("config.json", 'w') as f:
        json.dump(config, f)
