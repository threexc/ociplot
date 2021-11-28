#!/usr/bin/python3 
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import walksignal.utils as utils
from dataclasses import dataclass

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
class BaseStation:
    """Class containing basic information about a base station."""

    lat: float
    lon: float

    def get_distances(self, points):
        return [utils.get_distance(self.lat, self.lon, point.lat, point.lon) for point in points]

class MeasurementSet:
    """Class containing the measured data info."""

    def __init__(self, datafile):
        self.datafile = datafile
        self.data = pd.read_csv(datafile).drop('bid', axis=1).drop('sid', axis=1).drop('nid', axis=1).drop('psc', axis=1)
        self.summary = self.data.drop(['measured_at', 'pci', 'mcc', 'mnc', 'lac', 'cellid', 'tac', 'direction', 'ta'], axis=1).describe().apply(lambda s: s.apply('{0:.6f}'.format))
        self.rx_power = self.data['signal'].describe()

class MeasurementMultiSet:
    """Class containing an aggregate of MeasurementSet data"""
    
    def __init__(self, file_list):
        self.file_list = file_list
        self.sets = [MeasurementSet(f) for f in self.file_list]
        self.set_summaries = [mset.summary for mset in self.sets]
        self.data = pd.concat([mset.data for mset in self.sets], ignore_index=True)

        self.mobile_country_codes = self.data['mcc']
        self.mobile_network_codes = self.data['mnc']
        self.local_area_codes = self.data['lac']
        self.cellids = self.data['cellid']
        self.unique_mobile_country_codes = self.mobile_country_codes.unique()
        self.unique_mobile_network_codes = self.mobile_network_codes.unique()
        self.unique_local_area_codes = self.local_area_codes.unique()
        self.unique_cellids = self.cellids.unique()
        self.cellid_subsets = [self.data.loc[self.data['cellid'] == cellid] for cellid in self.unique_cellids]
        self.cellid_subset_summaries = [subset.drop(['measured_at', 'pci', 'mcc', 'mnc', 'lac', 'cellid', 'tac', 'direction', 'ta'], axis=1).describe() for subset in self.cellid_subsets]
        self.summary = self.data.drop(['measured_at', 'pci', 'mcc', 'mnc', 'lac', 'cellid', 'tac', 'direction', 'ta'], axis=1).describe().apply(lambda s: s.apply('{0:.6f}'.format))
        self.measured_cells = self.get_measured_cell_list()
        self.map_path = self.data_path() + "/map.png"
        self.bbox_path = self.data_path() + "/bbox.txt"
        self.cellmap = CellMap(self.map_path, self.bbox_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()
        self.cm = pyplot.cm.get_cmap('gist_heat')

    def data_path(self):
        return self.file_list[0].rsplit('/', 1)[0]

    """Return a list of all cells in the data matrix and their measured characteristics."""
    def get_measured_cell_list(self):
        return [MeasuredCell(self.data.loc[self.data['cellid'] == cellid], cellid) for cellid in self.data['cellid'].unique()]

    """Get the MeasuredCell matching a particular cellid."""
    def get_cell(self, cellid):
        for cell in self.measured_cells:
            if str(cell.cellid) == cellid:
                return cell

@dataclass
class Bitrate:
    """A class that stores a single datapoint of speed test data 
    extracted from a given row of a Pandas dataframe."""
    def __init__(self, point):
        self.type = point['type']
        self.ping = point['ping']
        self.jitter = point['jitter']
        self.down = point['down']
        self.up = point['up']
        self.time = point['time']
        self.lat = point['lat']
        self.lon = point['lon']
        self.accuracy = point['accuracy']

class BitrateSet:
    """A set of speed test data extracted from a Pandas dataframe."""

    def __init__(self, datafile):
        self.datafile = datafile
        self.data = pd.read_csv(self.datafile)
        self.summary = self.data.describe()

    def data_path(self):
        return self.datafile[0].rsplit('/', 1)[0]

    def get_points(self):
        return [Bitrate(row) for index, row in self.data.iterrows()]

    def get_mean(self, field):
        return self.data[field].mean()

    def get_max(self, field):
        return self.data[field].max()

    def get_min(self, field):
        return self.data[field].min()

class BitrateMultiSet:
    """Collection of BitrateSets."""

    def __init__(self, file_list):
        self.file_list = file_list
        self.sets = [BitrateSet(f) for f in self.file_list]
        self.set_summaries = [brset.summary for brset in self.sets]
        self.data = pd.concat([brset.data for brset in self.sets], ignore_index=True)
        self.summary = self.data.describe()
        self.map_path = self.data_path() + "/map.png"
        self.bbox_path = self.data_path() + "/bbox.txt"
        self.cellmap = CellMap(self.map_path, self.bbox_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()

    def data_path(self):
        return self.file_list[0].rsplit('/', 1)[0]

    def get_points(self):
        return [Bitrate(row) for index, row in self.data.iterrows()]

    def get_mean(self, field):
        return self.data[field].mean()

    def get_max(self, field):
        return self.data[field].max()

    def get_min(self, field):
        return self.data[field].min()
