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
