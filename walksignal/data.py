#!/usr/bin/python3 
import csv
import sys
import numpy as np
import pandas as pd
import time
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.utils as utils

class DataSet:
    def __init__(self, data, reference):
        self.data_file = data
        self.data_path = self.data_file[0].rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.reference_file = reference
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"

        self.loadDataset()
        self.loadReference()
        self.loadCells()
        self.loadPlot()

    def loadDataset(self):
        self.start_time = time.time()
        self.data_matrix = pd.concat([pd.read_csv(f) for f in self.data_file], ignore_index=True)
        self.duration = time.time() - self.start_time
        print("Done loading data_matrix in {:.2f} seconds".format(self.duration))

        self.start_time = time.time()
        self.time_range = np.array(self.data_matrix['measured_at'], dtype=float)
        self.data_start_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))
        self.data_end_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))
        self.normalized_time_range = (self.time_range - self.time_range[0])/1000
        self.lat = np.array(self.data_matrix['lat'], dtype=float)
        self.lon = np.array(self.data_matrix['lon'], dtype=float)
        self.signal = np.array(self.data_matrix['signal'], dtype=float)
        self.pcis = np.array(self.data_matrix['pci'], dtype=float)
        self.speed = np.array(self.data_matrix['speed'], dtype=float)
        self.mcc = np.array(self.data_matrix['mcc'], dtype=int)
        self.mnc = np.array(self.data_matrix['mnc'], dtype=int)
        self.lac = np.array(self.data_matrix['lac'], dtype=int)
        self.cellid = np.array(self.data_matrix['cellid'], dtype=int)
        self.mcc_u = np.unique(self.mcc)
        self.mnc_u = np.unique(self.mnc)
        self.lac_u = np.unique(self.lac)
        self.cellid_u = np.unique(self.cellid)
        self.rating = np.array(self.data_matrix['rating'], dtype=float)
        self.direction = np.array(self.data_matrix['direction'], dtype=float)
        self.timing_advance = np.array(self.data_matrix['ta'], dtype=float)
        self.access_type = self.data_matrix['act']
        self.access_type_color_codes = np.zeros(len(self.access_type),dtype="str")
        for x in range(len(self.access_type)):
            if self.access_type[x] == "LTE":
                self.access_type_color_codes[x] = "r"
            elif self.access_type[x] == "LTE+":
                self.access_type_color_codes[x] = "b"
            elif self.access_type[x] == "UMTS":
                self.access_type_color_codes[x] = "g"
            elif self.access_type[x] == "HSPA+":
                self.access_type_color_codes[x] = "k"
            else:
                self.access_type_color_codes[x] = "y"

        self.duration = time.time() - self.start_time
        print("Done loading dataset properties in {:.2f} seconds".format(self.duration))

    def loadReference(self):
        self.start_time = time.time()
        self.reference_matrix = pd.read_csv(self.reference_file)
        self.reference_matrix = self.reference_matrix.loc[self.reference_matrix['cell'].isin(self.cellid_u)]
        self.duration = time.time() - self.start_time
        print("Done loading reference_matrix in {:.2f} seconds".format(self.duration))

        self.start_time = time.time()
        self.ref_mcc = np.array(self.reference_matrix['mcc'])
        self.ref_mnc = np.array(self.reference_matrix['net'])
        self.ref_lac = np.array(self.reference_matrix['area'])
        self.ref_cellid = np.array(self.reference_matrix['cell'])
        self.ref_lon = np.array(self.reference_matrix['lon'])
        self.ref_lat = np.array(self.reference_matrix['lat'])
        self.ref_access = np.array(self.reference_matrix['radio'])
        self.duration = time.time() - self.start_time
        print("Done loading reference properties in {:.2f} seconds".format(self.duration))

    def loadCells(self):
        self.start_time = time.time()
        self.cell_id_list = []
        self.cell_list = []
        self.lat_data = self.lat
        self.lon_data = self.lon
        self.get_cell_ids()
        self.get_dataset_cell_data()
        self.get_cell_data_points()
        self.get_distances_to_cells()
        self.get_power()
        self.get_path_loss(43) # 43dBm or ~20W for 4G antenna
        self.cell_lat_data = self.get_cell_lats()
        self.cell_lon_data = self.get_cell_lons()
        self.duration = time.time() - self.start_time
        print("Done loading cell properties in {:.2f} seconds".format(self.duration))

    def loadPlot(self):
        self.start_time = time.time()
        self.plot_map = None
        self.map_bbox = None
        self.get_map_and_bbox()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.plotrange = np.linspace(1, 1500, 500)
        self.duration = time.time() - self.start_time
        print("Done loading plot properties in {:.2f} seconds".format(self.duration))


    def get_map_and_bbox(self):
        self.plot_map = plt.imread(self.map_path)
        self.map_bbox = [entry for entry in utils.get_bbox(self.bbox_path)]

    def get_cell_ids(self):
        for row in range(len(self.cellid_u)):
            self.cell_id_list.append((self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]))

    def get_dataset_cell_data(self):
        for cell_id in self.cell_id_list:
            if cell_id[3] in self.reference_matrix['cell'].unique():
                print("Found {0} in reference".format(cell_id[3]))
                for index, row in self.reference_matrix.iterrows():
                    if row['cell'] == cell_id[3]:
                        print("Added {0}".format(row['cell']))
                        self.cell_list.append(Cell(row['radio'], row['mcc'], row['net'], row['area'], row['cell'], row['lon'], row['lat'], row['range'], row['samples']))
            else:
                self.cell_list.append(Cell(mcc=cell_id[0], mnc=cell_id[1], lac=cell_id[2], cellid=cell_id[3]))

    def get_cell_data_points(self):
        for index, row in self.data_matrix.iterrows():
            for cell in self.cell_list:
                if (cell.cellid == row['cellid']):
                    cell.data_points.append(CellDataPoint(row['mcc'],
                        row['mnc'], row['lac'], row['cellid'],
                        row['lat'], row['lon'], row['signal'],
                        row['measured_at'], row['rating'],
                        row['speed'], row['direction'],
                        row['act'], row['ta'],
                        row['pci']))

    def get_distances_to_cells(self):
        for cell in self.cell_list:
            cell.get_distances()

    def get_power(self):
        for cell in self.cell_list:
            for datapoint in cell.data_points:
                cell.signal_power.append(float(datapoint.signal))

    def get_path_loss(self, tx_power):
        for cell in self.cell_list:
            cell.get_path_loss(tx_power)

    def get_cell_lats(self):
        cell_lats = [cell.lat for cell in self.cell_list]
        return cell_lats

    def get_cell_lons(self):
        cell_lons = [cell.lon for cell in self.cell_list]
        return cell_lons

    def get_cell_stats(self, mcc, mnc, lac, cellid):
        for cell in self.cell_list:
            if ((str(cell.mcc) == mcc) and (str(cell.mnc) == mnc) and (str(cell.lac) == lac) and (str(cell.cellid) == cellid)):
                print(cell.cellid)
                print(cell.lat, cell.lon)
                return cell

class Cell:
    def __init__(self, signal_type=None, mcc=None, mnc=None, lac=None, cellid=None, lon=None, lat=None, cell_range=None, samples=None):
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cellid = cellid
        self.lat = lat
        self.lon = lon
        self.range = cell_range
        self.samples = samples
        self.signal_type = signal_type
        self.data_points = []
        self.distances = []
        self.signal_power = []
        self.peak_value = None
        self.path_loss = []

    def get_distances(self):
        self.distances.clear()
        if (self.lat is None) or (self.lon is None):
            print("Can't get distances for {0} {1} {2} {3}, lat/lon not available".format(self.mcc, self.mnc, self.lac, self.cellid))
        else:
            for datapoint in self.data_points:
                self.distances.append(utils.get_distance(self.lat, self.lon, datapoint.lat, datapoint.lon) * 1000)

    def get_path_loss(self, tx_power):
        self.path_loss.clear()
        #self.peak_value = max(self.signal_power)
        self.path_loss = [tx_power - xi for xi in self.signal_power]

class CellDataPoint:
    def __init__(self, mcc, mnc, lac, cellid, lat, lon, signal, measured_at, rating, speed, direction, access_type, timing_advance, pci):
      self.mcc = mcc
      self.mnc = mnc
      self.lac = lac
      self.cellid = cellid
      self.lat = lat
      self.lon = lon
      self.signal = signal
      self.measured_at = measured_at
      self.rating = rating
      self.speed = speed
      self.direction = direction
      self.access_type = access_type
      self.timing_advance = timing_advance
      self.pci = pci
