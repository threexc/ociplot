#!/usr/bin/python3 
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import walksignal.utils as utils
from dataclasses import dataclass

class DataSet:
    """Class for loading and grooming OpenCellID formatted data and related files."""
    def __init__(self, data):
        self.measurements = MeasurementMultiSet(data)
        self.map_path = self.measurements.data_path() + "/map.png"
        self.bbox_path = self.measurements.data_path() + "/bbox.txt"

        self.mcc = np.array(self.measurements.data['mcc'], dtype=int)
        self.mnc = np.array(self.measurements.data['mnc'], dtype=int)
        self.lac = np.array(self.measurements.data['lac'], dtype=int)
        self.cellid = np.array(self.measurements.data['cellid'], dtype=int)
        self.mcc_u = np.unique(self.mcc)
        self.mnc_u = np.unique(self.mnc)
        self.lac_u = np.unique(self.lac)
        self.cellid_u = np.unique(self.cellid)

        self.measured_cells = self.get_measured_cell_list()

        self.cell_id_list = [(self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]) for row in range(len(self.cellid_u))]

        self.cellmap = CellMap(self.map_path, self.bbox_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()
        self.cm = pyplot.cm.get_cmap('gist_heat')
        self.plotrange = np.linspace(1, 1500, 500)

    def get_cell(self, cellid):
        for cell in self.measured_cells:
            if str(cell.cellid) == cellid:
                return cell

    """Get a tuple consisting of a cell's MCC, MNC, LAC, and Cell ID respectively."""
    def get_cell_ids(self):
        return [(self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]) for row in range(len(self.cellid_u))]

    """Return a list of all cells in the data matrix and their measured characteristics."""
    def get_measured_cell_list(self):
        return [MeasuredCell(self.measurements.data.loc[self.measurements.data['cellid'] == cellid], cellid) for cellid in self.cellid_u]

class MeasuredCell:
    """Class containing the complete set of data for a single cell."""
    def __init__(self, data, cellid):
        self.cellid = cellid
        self.distances = []
        self.ta = data['ta']
        self.mcc = data['mcc']
        self.mnc = data['mnc']
        self.lac = data['lac']
        self.lat = data['lat']
        self.lon = data['lon']
        self.act = data['act']
        self.tac = data['tac']
        self.pci = data['pci']
        self.speed = data['speed']
        self.rating = data['rating']
        self.signal_power = data['signal']
        self.direction = data['direction']
        self.measured_at = data['measured_at']
        self.peak_value = None
        self.path_loss = []
        self.data_points = [CellDataPoint(row) for index, row in data.iterrows()]

    def get_distances(self, tower_lat, tower_lon):
        return [utils.get_distance(tower_lat, tower_lon, data_point.lat, data_point.lon) * 1000 for data_point in self.data_points]

    def get_path_loss(self, tx_power):
        return [tx_power - xi for xi in self.signal_power]

class CellDataPoint:
    """Class containing the contents of a signal data point."""
    def __init__(self, datapoint):
      self.mcc = datapoint['mcc']
      self.mnc = datapoint['mnc']
      self.lac = datapoint['lac']
      self.lat = datapoint['lat']
      self.lon = datapoint['lon']
      self.pci = datapoint['pci']
      self.speed = datapoint['speed']
      self.cellid = datapoint['cellid']
      self.signal = datapoint['signal']
      self.rating = datapoint['rating']
      self.access_type = datapoint['act']
      self.timing_advance = datapoint['ta']
      self.direction = datapoint['direction']
      self.measured_at = datapoint['measured_at']

@dataclass
class CellMap:
    """Class containing OpenStreetMap imagery info."""
    map_path: str
    bbox_path: str

    def get_map(self):
        return pyplot.imread(self.map_path)

    def get_bbox(self):
        return [entry for entry in utils.get_bbox(self.bbox_path)]

@dataclass
class CellID:
    """Class containing cell identification information."""
    mcc: int
    mnc: int
    lac: int
    cellid: int

@dataclass
class BaseStation:
    """Class containing basic information about a base station."""

    lat: float
    lon: float

    def get_distances(self, points):
        return [utils.get_distance(self.lat, self.lon, point.lat, point.lon) for point in points]

@dataclass
class MeasurementSet:
    """Class containing the measured data info."""

    def __init__(self, datafile):
        self.datafile = datafile
        self.data = pd.read_csv(datafile).drop('bid', axis=1).drop('sid', axis=1).drop('nid', axis=1).drop('psc', axis=1)
        self.summary = self.data.describe()
        self.rx_power = self.data['signal'].describe()

class MeasurementMultiSet:
    """Class containing an aggregate of MeasurementSet data"""
    
    def __init__(self, file_list):
        self.file_list = file_list
        self.sets = [MeasurementSet(f) for f in self.file_list]
        self.set_summaries = [mset.summary for mset in self.sets]
        self.data = pd.concat([mset.data for mset in self.sets], ignore_index=True)
        self.summary = self.data.describe()
        print(self.summary)
        for summary in self.set_summaries:
            print(summary)

    def data_path(self):
        return self.file_list[0].rsplit('/', 1)[0]
