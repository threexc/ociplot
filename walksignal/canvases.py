#!/usr/bin/python3 
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
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

class SignalCanvas(MplCanvas):
    """Custom canvas class for drawing a map of tower positions and signal data
    points."""
    def __init__(self, parent=None, width=5, height=4, dpi=100,
            areamap=None):
        self.tower_list = {}
        self.cell_list = {}
        self.marker_list = {}
        self.areamap = areamap
        self.scalebar = None
        self.cmap = plt.cm.get_cmap("gist_heat")
        super(SignalCanvas, self).__init__()

    def addTower(self, tower):
        self.tower_list[tower.label] = tower

    def addCell(self, cell):
        self.cell_list[cell.label] = cell

    def addMarker(self, marker):
        self.marker_list[marker.label] = marker

    def removeTower(self, tower):
        del self.tower_list[tower.label]

    def removeCell(self, cell):
        del self.cell_list[cell.label]

    def removeMarker(self, marker):
        del self.market_list[marker.label]

    def clearTowers(self):
        self.tower_list.clear()

    def clearCells(self):
        self.cell_list.clear()

    def clearMarkers(self):
        self.marker_list.clear()

    def setMap(self, areamap):
        self.areamap = areamap

    def setScaleBar(self):
        x1, x2, y1, y2 = self.axes.axis()
        _y = (y1 + y2)/2
        p1, p2 = (int(x1), _y), (int(x1)+1, _y)
        meters_per_deg = utils.get_great_circle_distance(p1, p2).meters
        dist = utils.get_distance(self.areamap.bbox[0][2],
                 self.areamap.bbox[0][0],
                 self.areamap.bbox[0][2],
                 self.areamap.bbox[0][1])
        self.scalebar = ScaleBar(meters_per_deg, "m",
                length_fraction=0.2, location="lower right")

    def drawTower(self, tower):
        self.axes.scatter(tower.lon, tower.lat, zorder=1, alpha=1.0,
                s=32, color="blue")
        self.axes.annotate(tower.label, tower.lon, tower.lat,
                fontsize=14)

    def drawCell(self, cell):
        self.axes.scatter(cell.lon_array, cell.lat_array, zorder=1,
                alpha=1.0, s=20, c=cell.power_array, cmap=self.cmap)

    def drawMarker(self, marker):
        self.axes.scatter(marker.lon, marker.lat, zorder=1, alpha=1.0,
                s=32, color="black")
        self.axes.annotate(marker.label, marker.lon, marker.lat,
                fontsize=14)

    def redraw(self, cell):
        self.axes.cla()
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        self.axes.imshow(self.cellmap.get_map(), zorder=0, extent = self.map_extent, aspect="equal")
        powerscatter = self.drawCell(cell)
        towerscatter = [self.drawTower(tower_list[tower]) for tower in
                self.tower_list]
        markerscatter = [self.drawMarker(marker_list[marker]) for marker in
            self.marker_list]
        self.axes.set_xlim(self.map_extent[0], self.map_extent[1])
        self.axes.set_ylim(self.map_extent[2], self.map_extent[3])
        self.axes.set_xlabel("Longitude")
        self.axes.set_ylabel("Latitude")
        self.axes.set_title("Signal Power vs Position")
        self.axes.ticklabel_format(useOffset=False)
        self.axes.add_artist(self.scalebar)
        self.cbar = self.fig.colorbar(powerscatter, cax=cax)
        self.cbar.ax.set_ylabel("Signal Power (dBm)", rotation=270, labelpad=10)

        self.draw()
