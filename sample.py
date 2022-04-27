from dataclasses import dataclass, field
import numpy as np
import scanning_tools

@dataclass
class Sample:
    gisaxs_data: np.ndarray = field(default_factory=list)
    vertical_scan_x: list[float] = field(default_factory=list)
    vertical_scan_y: list[float] = field(default_factory=list)
    horizontal_scan_x: list[float] = field(default_factory=list)
    horizontal_scan_y: list[float] = field(default_factory=list)

    def get_x_angular(self):
        x_array = list(range(0, len(self.gisaxs_data[0])))
        x_theta_f = scanning_tools.convert_x(x_array)
        return x_theta_f

    def get_y_angular(self):
        data = self.gisaxs_data[::-1]
        y_array = list(range(0, len(data)))
        y_alpha_f = scanning_tools.convert_y(y_array)
        return y_alpha_f
