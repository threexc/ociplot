#!/usr/bin/python3 
import time
import statistics as stat
import numpy as np
import pandas as pd
import routesignal.utils as utils
from cellmap import CellMap

class Cell:
    """Class containing the complete set of data for a single cell."""
    def __init__(self, data, cellid):
        self.cellid = cellid
        columns = [
            "ta",
            "mcc",
            "mnc",
            "lac",
            "lat",
            "lon",
            "act",
            "tac",
            "pci",
            "speed",
            "rating",
            "signal",
            "direction",
            "measured_at",
        ]
        self.data = data[columns]
        self.power_mw = [np.power(10, (-1 * dBm) / 10) for dBm in self.data['signal']]

        self.geometric_average = stat.fmean(self.data['signal'])
        self.geometric_stdev_db = stat.stdev(self.data['signal'])

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
    def __init__(self, datafiles):
        self.datafiles = datafiles
        self.data = pd.concat([pd.read_csv(datafile).drop(['bid', 'sid', 'nid', 'psc'], axis=1) for datafile in datafiles])

        self.mobile_country_codes = self.data['mcc']
        self.mobile_network_codes = self.data['mnc']
        self.local_area_codes = self.data['lac']
        self.cellids = self.data['cellid']
        self.unique_mobile_country_codes = self.mobile_country_codes.unique()
        self.unique_mobile_network_codes = self.mobile_network_codes.unique()
        self.unique_local_area_codes = self.local_area_codes.unique()
        self.unique_cellids = self.cellids.unique()
        self.cells = {}

        for cellid in self.data['cellid'].unique():
            self.cells[cellid] = Cell(self.data.loc[self.data['cellid'] ==
                cellid], cellid)

        self.signal_power = pd.concat([cell.data['signal'] for key, cell in self.cells.items()])

        self.power_mw = [np.power(10, (-1 * dBm) / 10) for dBm in self.signal_power]

        self.geometric_average = stat.fmean(self.signal_power)
        self.geometric_stdev_db = stat.stdev(self.signal_power)

        print(f"geo average: {self.geometric_average} dBm")
        print(f"geo stdev: {self.geometric_stdev_db} dB")

        self.map_path = self.data_path() + "/map.png"
        self.bbox_path = self.data_path() + "/bbox.txt"
        self.cellmap = CellMap(self.map_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()

    def data_path(self):
        return self.datafiles[0].rsplit('/', 1)[0]

    """Get the Cell matching a particular cellid."""
    def get_cell(self, cellid):
        return self.cells[int(cellid)]

    def get_path_loss(self, cellid, tx_power, tx_gain, rx_gain):
        return [tx_power - xi - tx_gain - rx_gain for xi in self.cells[int(cellid)].data['signal']]

    def get_signal_power(self, cellid):
        return [xi for xi in self.cells[int(cellid)].data['signal']]

    def get_distances(self, cellid, tower_lat, tower_lon, bs_height):
        return [np.sqrt(np.square(bs_height) +
            np.square(utils.get_distance(tower_lat, tower_lon, data_point.lat,
                data_point.lon) * 1000)) for index, data_point in self.cells[int(cellid)].data.iterrows()]
