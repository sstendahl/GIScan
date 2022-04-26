from dataclasses import dataclass, field

@dataclass
class ROI:
    x0: int = 0
    x1: int = 0
    y0: int = 0
    y1: int = 0