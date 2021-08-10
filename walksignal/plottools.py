#!/usr/bin/python3 
import matplotlib
matplotlib.use('Qt5Agg')
import walksignal.models as md
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod

class MplCanvas(FigureCanvas):
    """Custom canvas class for drawing a map of data points."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

@dataclass
class FreeSpaceLine:
    """Class containing information about a free space path loss model.
    It is also a parent class for other path loss models that use the
    free space model as a baseline."""
    name: str
    domain: List[float]
    xlabel: str
    ylabel: str
    colormap: str

    def get_pl(self, freq, tx_gain, rx_gain):
        return md.v_pl_fs(self.domain, freq) - tx_gain - rx_gain

@dataclass
class ABGLine(FreeSpaceLine):
    alpha: float
    beta: float
    gamma: float
    sigma: float

    def get_pl(self, freq, ref_dist, ref_freq, tx_gain, rx_gain):
        return md.v_pl_abg(self.domain, freq, alpha, beta, gamma, sigma, ref_dist, ref_freq) - tx_gain - rx_gain

@dataclass
class CILine(FreeSpaceLine):
    sigma: float
    exp: float

    def get_pl(self, freq, ref_freq, tx_gain, rx_gain):
        return md.v_pl_ci(self.domain, freq, sigma, exp, ref_freq) - tx_gain - rx_gain 
