#!/usr/bin/python3 
import time
import numpy as np
import pandas as pd
import os.path
import matplotlib.pyplot as pyplot
import walksignal.utils as utils
from dataclasses import dataclass

class Cell:
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

    def get_distances(self, tower_lat, tower_lon, bs_height):
        return [np.sqrt(np.square(bs_height) +
            np.square(utils.get_distance(tower_lat, tower_lon, data_point.lat,
                data_point.lon) * 1000)) for data_point in self.data_points]

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

class CellMap:
    """Class containing OpenStreetMap imagery info."""
    def __init__(self, map_path):
        self.map_path = map_path
        self.bbox_path = os.path.dirname(self.map_path) + "/bbox.txt"

    def get_map(self):
        return pyplot.imread(self.map_path)

    def get_bbox(self):
        bbox = None
        with open(self.bbox_path) as f:
            bbox = [tuple(map(float, i.split(','))) for i in f]
        return bbox

class Tower:
    """Class containing basic information about a tower."""
    def __init__(self, lat, lon, label, height=None):
        self.lat = lat
        self.lon = lon
        self.label = label
        self.height = height

    def get_distance(self, point):
        return utils.get_distance(self.lat, self.lon, point.lat, point.lon) 

    def get_distances(self, points):
        return [self.get_distance(point) for point in points]

class Dataset:
    """Class containing the measured data info."""
    def __init__(self, datafile):
        self.datafile = datafile
        self.data = pd.read_csv(datafile).drop('bid', axis=1).drop('sid', axis=1).drop('nid', axis=1).drop('psc', axis=1)
        self.summary = self.data.drop(['measured_at', 'pci', 'mcc', 'mnc', 'lac', 'cellid', 'tac', 'direction', 'ta'], axis=1).describe().apply(lambda s: s.apply('{0:.6f}'.format))
        self.rx_power = self.data['signal'].describe()

class DataSuperset:
    """Class containing an aggregate of Dataset data"""
    def __init__(self, file_list):
        self.file_list = file_list
        self.sets = [Dataset(f) for f in self.file_list]
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
        self.cells = {}

        for cellid in self.data['cellid'].unique():
            self.cells[cellid] = Cell(self.data.loc[self.data['cellid'] ==
                cellid], cellid)
        self.map_path = self.data_path() + "/map.png"
        self.bbox_path = self.data_path() + "/bbox.txt"
        self.cellmap = CellMap(self.map_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()
        self.cm = pyplot.cm.get_cmap('gist_heat')

    def data_path(self):
        return self.file_list[0].rsplit('/', 1)[0]

    """Get the Cell matching a particular cellid."""
    def get_cell(self, cellid):
        return self.cells[cellid]
