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

class DataSet:
    def __init__(self, data, reference):
        self.data_file = data
        self.data_path = self.data_file[0].rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.reference_file = reference
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"

        self.__loadDataset()
        self.__loadReference()
        self.__loadCells()
        self.__loadPlot()

    def __loadDataset(self):
        self.data_matrix = pd.concat([pd.read_csv(f) for f in self.data_file], ignore_index=True)
        self.time_range = np.array(self.data_matrix['measured_at'], dtype=float)
        self.lats = np.array(self.data_matrix['lat'], dtype=float)
        self.lons = np.array(self.data_matrix['lon'], dtype=float)
        self.signal = np.array(self.data_matrix['signal'], dtype=float)
        self.pcis = np.array(self.data_matrix['pci'], dtype=float)
        self.speed = np.array(self.data_matrix['speed'], dtype=float)
        self.mcc = np.array(self.data_matrix['mcc'], dtype=int)
        self.mnc = np.array(self.data_matrix['mnc'], dtype=int)
        self.lac = np.array(self.data_matrix['lac'], dtype=int)
        self.cellid = np.array(self.data_matrix['cellid'], dtype=int)
        self.rating = np.array(self.data_matrix['rating'], dtype=float)
        self.direction = np.array(self.data_matrix['direction'], dtype=float)
        self.timing_advance = np.array(self.data_matrix['ta'], dtype=float)
        self.access_type = self.data_matrix['act']

        self.data_start_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))
        self.data_end_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))
        self.normalized_time_range = (self.time_range - self.time_range[0])/1000

        self.mcc_u = np.unique(self.mcc)
        self.mnc_u = np.unique(self.mnc)
        self.lac_u = np.unique(self.lac)
        self.cellid_u = np.unique(self.cellid)

    def __loadReference(self):
        self.reference_matrix = pd.read_csv(self.reference_file)
        self.reference_matrix = self.reference_matrix.loc[self.reference_matrix['cell'].isin(self.cellid_u)]

        self.ref_mcc = np.array(self.reference_matrix['mcc'])
        self.ref_mnc = np.array(self.reference_matrix['net'])
        self.ref_lac = np.array(self.reference_matrix['area'])
        self.ref_cellid = np.array(self.reference_matrix['cell'])
        self.ref_lon = np.array(self.reference_matrix['lon'])
        self.ref_lat = np.array(self.reference_matrix['lat'])
        self.ref_access = np.array(self.reference_matrix['radio'])

    def __loadCells(self):
        self.cell_id_list = self.get_cell_ids()
        self.cell_list = self.get_dataset_cells()
        self.get_cell_measurements()
        self.get_power()

    def __loadPlot(self):
        self.plot_map = self.get_map()
        self.map_bbox = self.get_bbox()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.plotrange = np.linspace(1, 1500, 500)

    def get_map(self):
        return plt.imread(self.map_path)

    def get_bbox(self):
        return [entry for entry in utils.get_bbox(self.bbox_path)]

    # get a record of each unique cellid and its corresponding mcc,
    # mnc, lac
    def get_cell_ids(self):
        return [(self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]) for row in range(len(self.cellid_u))]

    # find dataset cellids (if any) in the reference and add them to the
    # list of cells
    def get_dataset_cells(self):
        cell_list = []
        for cell in self.cell_id_list:
            if cell[3] in self.cellid_u:
                for index, row in self.reference_matrix.iterrows():
                    if row['cell'] == cell[3]:
                        cell_list.append(Cell(row))
            else:
                cell_list.append(Cell(mcc=cell_id[0], mnc=cell_id[1], lac=cell_id[2], cellid=cell_id[3]))

        return cell_list

    # pair each cell in self.cell_list with its corresponding
    # measurement points in the dataset
    def get_cell_measurements(self):
        for index, row in self.data_matrix.iterrows():
            for cell in self.cell_list:
                if (cell.cellid == row['cellid']):
                    cell.data_points.append(CellDataPoint(row))

    def get_power(self):
        for cell in self.cell_list:
            for datapoint in cell.data_points:
                cell.signal_power.append(float(datapoint.signal))

    def get_path_loss(self, tx_power):
        for cell in self.cell_list:
            cell.get_path_loss(tx_power)

    # return the cell corresponding to a given mcc, mnc, lac, and cellid
    def get_cell_stats(self, mcc, mnc, lac, cellid):
        for cell in self.cell_list:
            if ((str(cell.mcc) == mcc) and (str(cell.mnc) == mnc) and (str(cell.lac) == lac) and (str(cell.cellid) == cellid)):
                return cell

class Cell:
    def __init__(self, record):
        self.mcc = record['mcc']
        self.mnc = record['net']
        self.lac = record['area']
        self.cellid = record['cell']
        self.lat = record['lat']
        self.lon = record['lon']
        self.range = record['range']
        self.samples = record['samples']
        self.signal_type = record['radio']
        self.data_points = []
        self.distances = []
        self.signal_power = []
        self.peak_value = None
        self.path_loss = []

    def get_distances(self, tower_lat, tower_lon):
        self.distances.clear()
        for datapoint in self.data_points:
            self.distances.append(utils.get_distance(tower_lat, tower_lon, datapoint.lat, datapoint.lon) * 1000)

    def get_path_loss(self, tx_power):
        self.path_loss.clear()
        self.path_loss = [tx_power - xi for xi in self.signal_power]

class CellDataPoint:
    def __init__(self, datapoint):
      self.mcc = datapoint['mcc']
      self.mnc = datapoint['mnc']
      self.lac = datapoint['lac']
      self.cellid = datapoint['cellid']
      self.lat = datapoint['lat']
      self.lon = datapoint['lon']
      self.signal = datapoint['signal']
      self.measured_at = datapoint['measured_at']
      self.rating = datapoint['rating']
      self.speed = datapoint['speed']
      self.direction = datapoint['direction']
      self.access_type = datapoint['act']
      self.timing_advance = datapoint['ta']
      self.pci = datapoint['pci']
