import yaml
import numpy as np
import pyqtgraph as pg
from random import randint

class Config:
    def __init__(self, filename):

        self.filename = filename
        try:
            with open(self.filename) as stream:
                self.data = yaml.safe_load(stream)
                self.signal_data_files = self.data.get("signal_data_files")
                self.tower_lat = self.data.get("tower_lat", None)
                self.tower_lon = self.data.get("tower_lon", None)
                self.tower_label = self.data.get("tower_label", "Tower")
                self.freq = self.data.get("freq", 50)
                self.alpha = self.data.get("alpha", 1)
                self.beta = self.data.get("beta", 1)
                self.gamma = self.data.get("gamma", 1)
                self.sigma = self.data.get("sigma", 1)
                self.pl_exp = self.data.get("pl_exp", 1)
                self.pl_exp_tworay = self.data.get("pl_exp_tworay", 1)
                self.ref_dist = self.data.get("ref_dist", 1)
                self.ref_pl = self.data.get("ref_pl", 80)
                self.ref_freq = self.data.get("ref_freq", 1000000000)
                self.tx_power = self.data.get("tx_power", 43)
                self.tx_gain = self.data.get("tx_gain", 3)
                self.rx_gain = self.data.get("rx_gain", 3)
                self.bs_height = self.data.get("bs_height", 1)
                self.ue_height = self.data.get("ue_height", 1)
                self.oh_correction_factor = self.data.get("oh_correction_factor", 1)
                self.large_city = self.data.get("large_city", True)
                self.path_gain = self.data.get("path_gain", False)
        except:
            print("Could not load {0}. Setting defaults...".format(self.filename))
            self.signal_data_files = None
            self.tower_lat = None
            self.tower_lon = None
            self.tower_label = "Tower"
            self.freq = 50
            self.alpha = 1
            self.beta = 1
            self.gamma = 1
            self.sigma = 1
            self.pl_exp = 1
            self.pl_exp_tworay = 1
            self.ref_dist = 1
            self.ref_pl = 80
            self.ref_freq = 1000000000
            self.tx_power = 43
            self.tx_gain = 3
            self.rx_gain = 3
            self.bs_height = 1
            self.ue_height = 1
            self.oh_correction_factor = 1
            self.large_city = True
            self.path_gain = False

    def save(self):
        with open(self.filename, "w") as stream:
            self.lastcfg = {
                'signal_data_files': self.signal_data_files,
                'freq': self.freq,
                'alpha': self.alpha,
                'beta': self.beta,
                'gamma': self.gamma,
                'sigma': self.sigma,
                'pl_exp': self.pl_exp,
                'pl_exp_tworay': self.pl_exp_tworay,
                'ref_dist': self.ref_dist,
                'ref_pl': self.ref_pl,
                'ref_freq': self.ref_freq,
                'tx_power': self.tx_power,
                'tx_gain': self.tx_gain,
                'rx_gain': self.rx_gain,
                'bs_height': self.bs_height,
                'ue_height': self.ue_height,
                'oh_correction_factor': self.oh_correction_factor,
                'large_city': self.large_city,
                'path_gain': self.path_gain
            }
            if self.tower_lat and self.tower_lon:
              self.lastcfg['tower_lat'] = self.tower_lat
              self.lastcfg['tower_lon'] = self.tower_lon
              if self.tower_label:
                  self.lastcfg['tower_label'] = self.tower_label

            yaml.dump(self.lastcfg, stream)
