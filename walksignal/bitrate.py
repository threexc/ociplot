#!/usr/bin/python3
import pandas as pd
from dataclasses import dataclass

@dataclass
class BitRate:
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

class BitRateSet:
    """A set of speed test data extracted from a Pandas dataframe."""
    def __init__(self, datafile):
        self.data = pd.read_csv(datafile)

    def get_points(self):
        return [BitRate(row) for index, row in self.data.iterrows()]

    def get_mean(self, field):
        return self.data[field].mean()

    def get_max(self, field):
        return self.data[field].max()

    def get_min(self, field):
        return self.data[field].min()

def main():
   bitrateset = BitRateSet("07022021.txt") 

   points = bitrateset.get_points()
   for point in points:
       print(point.down)

   print(bitrateset.get_mean("jitter"))
   print(bitrateset.get_mean("down"))
   print(bitrateset.get_max("down"))


if __name__ == "__main__":
    main()
