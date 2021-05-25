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
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"

        self.start_time = time.time()
        self.data_matrix = pd.concat([pd.read_csv(f) for f in data], ignore_index=True)
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

        self.start_time = time.time()
        self.reference_matrix = pd.read_csv(reference)
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

        self.start_time = time.time()
        self.tower_id_list = []
        self.tower_list = []
        self.lat_data = self.lat
        self.lon_data = self.lon
        self.get_tower_ids()
        self.get_dataset_tower_data()
        self.get_tower_data_points()
        self.get_distances_to_towers()
        self.get_power()
        self.get_path_loss()
        self.tower_lat_data = self.get_tower_lats()
        self.tower_lon_data = self.get_tower_lons()
        self.duration = time.time() - self.start_time
        print("Done loading tower properties in {:.2f} seconds".format(self.duration))

        self.start_time = time.time()
        self.plot_map = None
        self.map_bbox = None
        self.get_map_and_bbox()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.set_image()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.cm2 = plt.cm.get_cmap('gist_gray')
        self.avg_lat_diff = np.average(np.ediff1d(self.lat_data))
        self.avg_lon_diff = np.average(np.ediff1d(self.lon_data))
        self.distances = np.array([])
        self.plotrange = np.linspace(1, 1500, 500)
        self.duration = time.time() - self.start_time
        print("Done loading plot properties in {:.2f} seconds".format(self.duration))

    def get_map_and_bbox(self):
        self.plot_map = plt.imread(self.map_path)
        self.map_bbox = [entry for entry in utils.get_bbox(self.bbox_path)]

    def set_image(self):
        self.ax1.imshow(self.plot_map, zorder=0, extent = self.map_bbox[0], aspect="equal")

    def get_tower_ids(self):
        for row in range(len(self.cellid_u)):
            self.tower_id_list.append((self.mcc[row], self.mnc[row], self.lac[row], self.cellid_u[row]))

    def get_dataset_tower_data(self):
        for tower_id in self.tower_id_list:
            if tower_id[3] in self.reference_matrix['cell'].unique():
                print("Found {0} in reference".format(tower_id[3]))
                for index, row in self.reference_matrix.iterrows():
                    if row['cell'] == tower_id[3]:
                        print("Added {0}".format(row['cell']))
                        self.tower_list.append(Cell(row['radio'], row['mcc'], row['net'], row['area'], row['cell'], row['lon'], row['lat'], row['range'], row['samples']))
            else:
                self.tower_list.append(Cell(mcc=tower_id[0], mnc=tower_id[1], lac=tower_id[2], cellid=tower_id[3]))

    def get_tower_data_points(self):
        for index, row in self.data_matrix.iterrows():
            for tower in self.tower_list:
                if (tower.cellid == row['cellid']):
                    tower.data_points.append(CellDataPoint(row['mcc'],
                        row['mnc'], row['lac'], row['cellid'],
                        row['lat'], row['lon'], row['signal'],
                        row['measured_at'], row['rating'],
                        row['speed'], row['direction'],
                        row['act'], row['ta'],
                        row['pci']))

    def get_distances_to_towers(self):
        for tower in self.tower_list:
            tower.get_distances()

    def get_power(self):
        for tower in self.tower_list:
            for datapoint in tower.data_points:
                tower.signal_power.append(float(datapoint.signal))

    def get_path_loss(self):
        for tower in self.tower_list:
            tower.get_path_loss()

    def get_tower_lats(self):
        tower_lats = [tower.lat for tower in self.tower_list]
        return tower_lats

    def get_tower_lons(self):
        tower_lons = [tower.lon for tower in self.tower_list]
        return tower_lons

    def get_tower_stats(self, mcc, mnc, lac, cellid):
        for tower in self.tower_list:
            if ((str(tower.mcc) == mcc) and (str(tower.mnc) == mnc) and (str(tower.lac) == lac) and (str(tower.cellid) == cellid)):
                print(tower.cellid)
                print(tower.lat, tower.lon)
                return tower

class Cell:
    def __init__(self, signal_type=None, mcc=None, mnc=None, lac=None, cellid=None, lon=None, lat=None, tower_range=None, samples=None):
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cellid = cellid
        self.lat = lat
        self.lon = lon
        self.range = tower_range
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

    def get_path_loss(self):
        self.path_loss.clear()
        self.peak_value = max(self.signal_power)
        self.path_loss = [self.peak_value - xi for xi in self.signal_power]

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
