from dataclasses import dataclass, field
import numpy as np
import scanning_tools
import json
import os
import sys

@dataclass
class Sample:
    path: str = ""
    gisaxs_data: np.ndarray = field(default_factory=list)
    vertical_scan_x: list[float] = field(default_factory=list)
    vertical_scan_y: list[float] = field(default_factory=list)
    horizontal_scan_x: list[float] = field(default_factory=list)
    horizontal_scan_y: list[float] = field(default_factory=list)

    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.mapping = config["mapping"]
        self.ai = config["ai"]

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
