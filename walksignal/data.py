#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.utils as utils

class DataSet:
    def __init__(self, data, reference):
        self.data_file = data
        self.data_path = self.data_file.rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"
        self.data_matrix = np.array(utils.read_csv(data))
        self.reference_matrix = np.array(utils.read_csv(reference))

        # Determine start and end times of test and get a time range for the trip
        self.time_range = np.array(self.data_matrix[1:,7], dtype=float)
        self.start_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))
        self.end_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))
        self.normalized_time_range = (self.time_range - self.time_range[0])/1000
        self.lat = np.array(self.data_matrix[1:,4], dtype=float)
        self.lon = np.array(self.data_matrix[1:,5], dtype=float)

        # get signal strength in dBm
        self.signal_range = np.array(self.data_matrix[1:,6], dtype=float)

        # get physical cell IDs
        self.pcis = np.array(self.data_matrix[1:,15], dtype=float)

        # get device speed
        self.speed_values = np.array(self.data_matrix[1:,9], dtype=float)
        self.mcc = np.array(self.data_matrix[1:,0], dtype=int)
        self.mnc = np.array(self.data_matrix[1:,1], dtype=int)
        self.lac = np.array(self.data_matrix[1:,2], dtype=int)
        self.cellid = np.array(self.data_matrix[1:,3], dtype=int)
        self.rating = np.array(self.data_matrix[1:,8], dtype=float)
        self.direction = np.array(self.data_matrix[1:,10], dtype=float)
        self.timing_advance = np.array(self.data_matrix[1:,12], dtype=float)

        # get access types and convert them to usable format
        self.access_type_range = np.array(self.data_matrix[1:,11])
        self.access_type_color_codes = np.zeros(len(self.access_type_range), dtype="str")
        for x in range(len(self.access_type_range)):
            if self.access_type_range[x] == "LTE":
                self.access_type_color_codes[x] = "r"
            elif self.access_type_range[x] == "LTE+":
                self.access_type_color_codes[x] = "b"
            elif self.access_type_range[x] == "UMTS":
                self.access_type_color_codes[x] = "g"
            elif self.access_type_range[x] == "HSPA+":
                self.access_type_color_codes[x] = "k"
            else:
                self.access_type_color_codes[x] = "y"

        self.hash = {}
        self.hash['time'] = self.normalized_time_range
        self.hash['signal_strength'] = self.signal_range
        self.hash['pcis'] = self.pcis
        self.hash['speed'] = self.speed_values
        self.hash['mcc'] = self.mcc
        self.hash['mnc'] = self.mnc
        self.hash['lac'] = self.lac
        self.hash['cellid'] = self.cellid
        self.hash['rating'] = self.rating
        self.hash['direction'] = self.direction
        self.hash['advance'] = self.timing_advance

        self.tower_list = TowerList(self.data_matrix, self.reference_matrix)
        self.tower_lat_data = self.tower_list.lats
        self.tower_lon_data = self.tower_list.lons
        self.lat_data = self.lat
        self.lon_data = self.lon
        self.signal_data = self.signal_range
        self.mcc_u = np.unique(self.mcc)
        self.mnc_u = np.unique(self.mnc)
        self.lac_u = np.unique(self.lac)
        self.cellid_u = np.unique(self.cellid)
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
        self.plotrange = np.linspace(1, 500, 250)

    def get_map_and_bbox(self):
        self.plot_map = plt.imread(self.map_path)
        self.map_bbox = [entry for entry in utils.get_bbox(self.bbox_path)]

    def set_image(self):
        self.ax1.imshow(self.plot_map, zorder=0, extent = self.map_bbox[0], aspect="equal")

class TowerList:
    def __init__(self, data, reference):
        self.tower_id_list = []
        self.tower_list = []
        self.cellid_list = []
        self.data = np.array(data)
        self.lats = np.array([])
        self.lons = np.array([])

        self.reference_data = np.array(reference)

        # Fill tower_id_list with tuples of mcc, mnc, lac, cellid
        self.get_tower_ids()

        # Add detected towers to the tower_list by comparing mcc, mnc,
        # lac, cellid with the reference file
        self.get_towers()

        # Add all relevant datapoints to each tower's data_points list
        self.get_tower_data_points()
        self.get_distances()
        self.get_power()
        self.get_tower_lats()
        self.get_tower_lons()

    def get_tower_ids(self):
        for row in self.data:
            if row[3] not in self.cellid_list:
                self.cellid_list.append(row[3])
                self.tower_id_list.append((row[0], row[1], row[2], row[3]))

    def get_towers(self):
        for row in self.reference_data:
            for entry in self.tower_id_list:
                if ((row[1] == entry[0]) and (row[2] == entry[1]) and (row[3] == entry[2]) and (row[4] == entry[3])):
                    self.tower_list.append(Tower(row[0], row[1], row[2], row[3], row[4], row[6], row[7], row[8], row[9]))

    def get_tower_data_points(self):
        for tower in self.tower_list:
            for row in self.data:
                if ((tower.mcc == row[0]) and (tower.mnc == row[1]) and (tower.lac == row[2]) and (tower.cellid == row[3])):
                    tower.data_points.append(TowerDataPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[14], row[15]))

    def get_distances(self):
        for tower in self.tower_list:
            tower.get_distances()

    def get_power(self):
        for tower in self.tower_list:
            for datapoint in tower.data_points:
                tower.signal_power.append(float(datapoint.signal))

    def get_tower_lats(self):
        for tower in self.tower_list:
            self.lats = np.concatenate([self.lats, [float(tower.lat)]])

    def get_tower_lons(self):
        for tower in self.tower_list:
            self.lons = np.concatenate([self.lons, [float(tower.lon)]])

    def get_tower_data(self, mcc, mnc, lac, cellid):
        for tower in self.tower_list:
            if ((tower.mcc == mcc) and (tower.mnc == mnc) and (tower.lac == lac) and (tower.cellid == cellid)):
                return tower

class Tower:
    def __init__(self, signal_type, mcc, mnc, lac, cellid, lon, lat, tower_range, samples):
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

    def get_distances(self):
        self.distances.clear()
        for datapoint in self.data_points:
            self.distances.append(utils.get_distance(self.lat, self.lon, datapoint.lat, datapoint.lon) * 1000)

class TowerDataPoint:
    def __init__(self, mcc, mnc, lac, cellid, lat, lon, signal, measured_at, rating, speed, direction, access_type, timing_advance, tac, pci):
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
      self.tac = tac
      self.pci = pci
