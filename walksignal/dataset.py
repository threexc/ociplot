#!/usr/bin/python3 
import csv
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import walksignal.utils as utils
from mpl_toolkits.axes_grid1 import make_axes_locatable
from dataclasses import dataclass
from abc import ABC

class DataSet:
    def __init__(self, data, reference):
        self.measurements = MeasurementSet(data)
        self.reference = ReferenceSet(reference)
        self.map_path = self.measurements.data_path() + "/map.png"
        self.bbox_path = self.measurements.data_path() + "/bbox.txt"

        self.data_matrix = self.measurements.data_matrix()

        self.mcc = self.m_mcc()
        self.mnc = self.m_mnc()
        self.lac = self.m_lac()
        self.cellid = self.m_cellid()
        self.mcc_u = np.unique(self.m_mcc())
        self.mnc_u = np.unique(self.m_mnc())
        self.lac_u = np.unique(self.m_lac())
        self.cellid_u = np.unique(self.m_cellid())

        self.measured_cells = self.get_measured_cell_list()

        self.reference_matrix = self.reference.reference_matrix()
        # Only deal with reference entries that show up in the
        # measurement set
        self.reference_matrix = self.reference_matrix.loc[self.reference_matrix['cell'].isin(self.cellid_u)]

        self.cell_id_list = self.get_cell_ids()
        self.ref_cells = self.get_ref_cells(self.cell_id_list)

        self.cellmap = CellMap(self.map_path, self.bbox_path)
        self.plot_map = self.cellmap.get_map()
        self.map_bbox = self.cellmap.get_bbox()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.plotrange = np.linspace(1, 1500, 500)

    def m_time_range(self):
        return np.array(self.data_matrix['measured_at'], dtype=float)

    def m_start_time(self):
        return time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))

    def m_end_time(self):
        return time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))

    def m_normalized_time_range(self):
        return (self.time_range - self.time_range[0])/1000
    
    def m_lats(self):
        return np.array(self.data_matrix['lat'], dtype=float)

    def m_lons(self):
        return np.array(self.data_matrix['lon'], dtype=float)

    def m_signal(self):
        return np.array(self.data_matrix['signal'], dtype=float)

    def m_pci(self):
        return np.array(self.data_matrix['pci'], dtype=float)

    def m_speed(self):
        return np.array(self.data_matrix['speed'], dtype=float)

    def m_mcc(self):
        return np.array(self.data_matrix['mcc'], dtype=int)

    def m_mnc(self):
        return np.array(self.data_matrix['mnc'], dtype=int)

    def m_lac(self):
        return np.array(self.data_matrix['lac'], dtype=int)

    def m_cellid(self):
        return np.array(self.data_matrix['cellid'], dtype=int)

    def m_rating(self):
        return np.array(self.data_matrix['rating'], dtype=float)

    def m_direction(self):
        return np.array(self.data_matrix['direction'], dtype=float)

    def m_ta(self):
        return np.array(self.data_matrix['ta'], dtype=float)

    def m_act(self):
        return self.data_matrix['act']

    def get_cell(self, cellid):
        for cell in self.measured_cells:
            if str(cell.cellid) == cellid:
                return cell

    # get a record of each unique cellid and its corresponding mcc,
    # mnc, lac
    def get_cell_ids(self):
        return [(self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]) for row in range(len(self.cellid_u))]

    # find dataset cellids (if any) in the reference and add them to the
    # list of cells
    def get_ref_cells(self, cellid_list):
        ref_cells = []
        for cell in cellid_list:
            for index, row in self.reference_matrix.iterrows():
                if row['cell'] == cell[3]:
                        ref_cells.append(RefCell(row))

        return ref_cells

    def get_measured_cell_list(self):
        return [MeasuredCell(self.data_matrix.loc[self.data_matrix['cellid'] == cellid], cellid) for cellid in self.cellid_u]

    def get_path_loss(self, tx_power):
        for cell in self.ref_cells:
            cell.get_path_loss(tx_power)

    # return the cell corresponding to a given mcc, mnc, lac, and cellid
    def get_cell_stats(self, mcc, mnc, lac, cellid):
        for cell in self.ref_cells:
            if ((str(cell.mcc) == mcc) and (str(cell.mnc) == mnc) and (str(cell.lac) == lac) and (str(cell.cellid) == cellid)):
                return cell

class MeasuredCell:
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
        self.distances.clear()
        for datapoint in self.data_points:
            self.distances.append(utils.get_distance(tower_lat, tower_lon, datapoint.lat, datapoint.lon) * 1000)

    def get_path_loss(self, tx_power):
        self.path_loss.clear()
        self.path_loss = [tx_power - xi for xi in self.signal_power]

class RefCell:
    def __init__(self, ref):
        self.mcc = ref['mcc']
        self.mnc = ref['net']
        self.lat = ref['lat']
        self.lon = ref['lon']
        self.lac = ref['area']
        self.cellid = ref['cell']
        self.range = ref['range']
        self.samples = ref['samples']
        self.signal_type = ref['radio']

class CellDataPoint:
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
        return plt.imread(self.map_path)

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

    data_file: str

    def data_path(self):
        return self.data_file[0].rsplit('/', 1)[0]

    def data_matrix(self):
        return pd.concat([pd.read_csv(f) for f in self.data_file], ignore_index=True)

@dataclass
class ReferenceSet:
    """Class containing the reference set info."""

    reference_file: str

    def reference_path(self):
        return self.reference_file[0].rsplit('/', 1)[0]

    def reference_matrix(self):
        return pd.read_csv(self.reference_file)
