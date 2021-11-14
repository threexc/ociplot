#!/usr/bin/python3
import pandas as pd
from dataclasses import dataclass

@dataclass
class Bitrate:
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

class BitrateSet:
    """A set of speed test data extracted from a Pandas dataframe."""

    def __init__(self, datafile):
        self.datafile = datafile
        self.data = pd.read_csv(self.datafile)
        self.summary = self.data.describe()

    def data_path(self):
        return self.datafile[0].rsplit('/', 1)[0]

    def get_points(self):
        return [Bitrate(row) for index, row in self.data.iterrows()]

    def get_mean(self, field):
        return self.data[field].mean()

    def get_max(self, field):
        return self.data[field].max()

    def get_min(self, field):
        return self.data[field].min()

class BitrateMultiSet:
    """Collection of BitrateSets."""

    def __init__(self, file_list):
        self.file_list = file_list
        self.sets = [BitrateSet(f) for f in self.file_list]
        self.set_summaries = [brset.summary for brset in self.sets]
        self.data = pd.concat([brset.data for brset in self.sets], ignore_index=True)
        self.summary = self.data.describe()
        print(self.summary)
        for summary in self.set_summaries:
            print(summary)

    def data_path(self):
        return self.file_list[0].rsplit('/', 1)[0]

    def get_points(self):
        return [Bitrate(row) for index, row in self.data.iterrows()]

    def get_mean(self, field):
        return self.data[field].mean()

    def get_max(self, field):
        return self.data[field].max()

    def get_min(self, field):
        return self.data[field].min()
