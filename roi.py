from dataclasses import dataclass, field
from matplotlib.patches import Rectangle

class ROI(Rectangle):
    """Class for the ROI boxes. Currently identical to matplotlibs Rectangle class, but may move some class specific
    methods here for instance."""
    pass