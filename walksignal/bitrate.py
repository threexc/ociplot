#!/usr/bin/python3
import csv
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from dataclasses import dataclass
from abc import ABC

class BitRate:
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

@dataclass
class BitRateSet:
    bitrate_file: str

    def get_bitrates(self):
        return pd.read_csv(self.bitrate_file)

    def get_bitrate_list(self):
        return [BitRate(row) for index, row in self.get_bitrates().iterrows()]

def main():
   bitrateset = BitRateSet("07022021.txt") 
   bitrates = bitrateset.get_bitrates()
   br_list = bitrateset.get_bitrate_list()

   print(br_list)

if __name__ == "__main__":
    main()


