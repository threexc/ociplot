import csv
import math
import utm
import os
import yaml
from geopy import distance

class Config:
    def __init__(self, config):
        if os.path.isfile(config):
            with open(config) as stream:
                self.loaded_data = yaml.safe_load(stream)
        else:
            self.loaded_data = None

    def get(self, prop):
        return self.loaded_data[prop] if prop in self.loaded_data else None

def read_csv(data_file):
      with open(data_file) as csv_file:
          data = list(csv.reader(csv_file, delimiter=","))
          csv_file.close()
      return data

def get_bbox(bbox_path):
      bbox = None
      with open(bbox_path) as f:
          bbox = [tuple(map(float, i.split(','))) for i in f]
      return bbox

def convert_to_xy(lat, lon):
    x, y, zn, zl = utm.from_latlon(lat, lon)
    return x, y, zn, zl

def convert_to_latlon(x, y, zn, zl):
    lat, lon = utm.to_latlon(x, y, zn, zl)
    return lat, lon

def advance_coordinates(x, y, speed, direction):
    # north is 0, east is 90
    x_advance = speed * -1 * math.cos(direction + math.pi/2)
    y_advance = speed * math.sin(direction + math.pi/2)
    adj_x = x + x_advance
    adj_y = y + y_advance

    return adj_x, adj_y

def project_next_position(lat, lon, speed, direction):
    x, y, zn, zl = convert_to_xy(lat, lon)
    adj_x, adj_y = advance_coordinates(x, y, speed, direction)
    lat_proj, lon_proj = convert_to_latlon(adj_x, adj_y, zn, zl)
    return lat_proj, lon_proj

def get_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6373.0
    coords_one = (lat1, lon1)
    coords_two = (lat2, lon2)

    return distance.distance(coords_one, coords_two).km

