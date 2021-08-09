#!/usr/bin/python3 
import matplotlib
matplotlib.use('Qt5Agg')
import walksignal.equations as eq
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

@dataclass
class FreeSpaceLine:
    name: str
    power: List[float]
    domain: List[float]
    xlabel: str
    ylabel: str
    colormap: str

    def get_pl(self, freq, tx_gain, rx_gain):
        return eq.v_pl_fs(self.power, freq, tx_gain, rx_gain)

@dataclass
class ABGLine(FreeSpaceLine):
    alpha: float
    beta: float
    gamma: float
    sigma: float

    def get_pl(self, freq, tx_gain, rx_gain):
        return eq.v_pl_abg(self.power, freq, alpha, beta, gamma, sigma,
                ref_dist, ref_freq, tx_gain, rx_gain)
