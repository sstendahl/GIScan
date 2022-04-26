from dataclasses import dataclass, field
import numpy as np

@dataclass
class Sample:
    gisaxs_data: np.ndarray = field(default_factory=list)
    vertical_scan_x: list[float] = field(default_factory=list)
    vertical_scan_y: list[float] = field(default_factory=list)
    horizontal_scan_x: list[float] = field(default_factory=list)
    horizontal_scan_y: list[float] = field(default_factory=list)
