from dataclasses import dataclass, field
import numpy as np
import scanning_tools
import json

@dataclass
class Sample:
    path: str = ""
    gisaxs_data: np.ndarray = field(default_factory=list)
    vertical_scan_x: list = field(default_factory=list)
    vertical_scan_y: list = field(default_factory=list)
    horizontal_scan_x: list = field(default_factory=list)
    horizontal_scan_y: list = field(default_factory=list)
    average_bg: int = 0

    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.mapping = config["mapping"]
        self.ai = config["ai"]
        self.vertical_scan_y = []
        self.vertical_scan_x = []
        self.horizontal_scan_y = []
        self.horizontal_scan_x = []

    def remove_background(self, heigth = 1, horizontal = True):
        if horizontal:
            self.horizontal_scan_y = [data - self.average_bg * heigth for data in self.horizontal_scan_y]
        else:
            self.vertical_scan_y = [data - self.average_bg*heigth for data in self.vertical_scan_y]

    def remove_zeroes(self):
        new_list = []
        new_coordinatelist = []
        for index in range(len(self.vertical_scan_y)):
            if self.vertical_scan_y[index] > 0:
                new_list.append(self.vertical_scan_y[index])
                new_coordinatelist.append(self.vertical_scan_x[index])

        self.vertical_scan_y = new_list
        self.vertical_scan_x = new_coordinatelist

        new_list = []
        new_coordinatelist = []
        for index in range(len(self.horizontal_scan_y)):
            if self.horizontal_scan_y[index] > 0:
                new_list.append(self.horizontal_scan_y[index])
                new_coordinatelist.append(self.horizontal_scan_x[index])

        self.horizontal_scan_y = new_list
        self.horizontal_scan_x = new_coordinatelist

    def get_x_pixels(self):
        x_array = list(range(0, len(self.gisaxs_data[0])))
        return x_array

    def get_y_pixels(self):
        data = self.gisaxs_data[::-1]
        y_array = list(range(0, len(data)))
        return y_array

    def get_x_angular(self):
        x_array = list(range(0, len(self.gisaxs_data[0])))
        x_theta_f = scanning_tools.convert_x(x_array)
        return x_theta_f

    def get_y_angular(self):
        data = self.gisaxs_data[::-1]
        y_array = list(range(0, len(data)))
        y_alpha_f = scanning_tools.convert_y(y_array)
        return y_alpha_f

    def get_y_qspace(self):
        ttheta_f = self.get_x_angular()
        alpha_f = self.get_y_angular()
        q_y = [(2*np.pi)/(0.96)*(np.cos(np.deg2rad(alpha_f))*np.sin(np.deg2rad(ttheta_f))) for alpha_f, ttheta_f in zip(alpha_f, ttheta_f)]
        return q_y

    def get_z_qspace(self):
        alpha_f = self.get_y_angular()
        alpha_i = self.ai
        q_y = [(2*np.pi)/(0.96)*(np.sin(np.deg2rad(alpha_f)) + np.sin(np.deg2rad(alpha_i))) for alpha_f in alpha_f]
        return q_y
