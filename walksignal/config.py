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
                self.bitrate_data_files = self.data.get("bitrate_data_files")
                self.tower_lat = self.data.get("tower_lat", None)
                self.tower_lon = self.data.get("tower_lon", None)
                self.pl_freq_value = self.data.get("pl_freq_value", 50)
                self.pl_alpha_value = self.data.get("pl_alpha_value", 1)
                self.pl_beta_value = self.data.get("pl_beta_value", 1)
                self.pl_gamma_value = self.data.get("pl_gamma_value", 1)
                self.pl_sigma_value = self.data.get("pl_sigma_value", 1)
                self.pl_exp_value = self.data.get("pl_exp_value", 1)
                self.pl_exp_tworay_value = self.data.get("pl_exp_tworay_value", 1)
                self.pl_ref_dist_value = self.data.get("pl_ref_dist_value", 1)
                self.pl_ref_pl_value = self.data.get("pl_ref_pl_value", 80)
                self.pl_ref_freq_value = self.data.get("pl_ref_freq_value", 1000000000)
                self.pl_tx_power_value = self.data.get("pl_tx_power_value", 43)
                self.pl_tx_gain_value = self.data.get("pl_tx_gain_value", 3)
                self.pl_rx_gain_value = self.data.get("pl_rx_gain_value", 3)
                self.pl_bs_height_value = self.data.get("pl_bs_height_value", 1)
                self.pl_ue_height_value = self.data.get("pl_ue_height_value", 1)
                self.pl_correction_factor = self.data.get("pl_correction_factor", 1)
                self.pl_large_city_state = self.data.get("pl_large_city_state", True)
                self.pl_path_gain_state = self.data.get("pl_path_gain_state", False)
        except:
            print("Could not load {0}. Setting defaults...".format(self.filename))
            self.signal_data_files = None
            self.bitrate_data_files = None
            self.tower_lat = None
            self.tower_lon = None
            self.pl_freq_value = 50
            self.pl_alpha_value = 1
            self.pl_beta_value = 1
            self.pl_gamma_value = 1
            self.pl_sigma_value = 1
            self.pl_exp_value = 1
            self.pl_exp_tworay_value = 1
            self.pl_ref_dist_value = 1
            self.pl_ref_pl_value = 80
            self.pl_ref_freq_value = 1000000000
            self.pl_tx_power_value = 43
            self.pl_tx_gain_value = 3
            self.pl_rx_gain_value = 3
            self.pl_bs_height_value = 1
            self.pl_ue_height_value = 1
            self.pl_correction_factor = 1
            self.pl_large_city_state = True
            self.pl_path_gain_state = False

    def save(self):
        with open(self.filename, "w") as stream:
            self.lastcfg = {
                'signal_data_files': self.signal_data_files,
                'bitrate_data_files': self.bitrate_data_files,
                'pl_freq_value': self.pl_freq_value,
                'pl_alpha_value': self.pl_alpha_value,
                'pl_beta_value': self.pl_beta_value,
                'pl_gamma_value': self.pl_gamma_value,
                'pl_sigma_value': self.pl_sigma_value,
                'pl_exp_value': self.pl_exp_value,
                'pl_exp_tworay_value': self.pl_exp_tworay_value,
                'pl_ref_dist_value': self.pl_ref_dist_value,
                'pl_ref_pl_value': self.pl_ref_pl_value,
                'pl_ref_freq_value': self.pl_ref_freq_value,
                'pl_tx_power_value': self.pl_tx_power_value,
                'pl_tx_gain_value': self.pl_tx_gain_value,
                'pl_rx_gain_value': self.pl_rx_gain_value,
                'pl_bs_height_value': self.pl_bs_height_value,
                'pl_ue_height_value': self.pl_ue_height_value,
                'pl_correction_factor': self.pl_correction_factor,
                'pl_large_city_state': self.pl_large_city_state,
                'pl_path_gain_state': self.pl_path_gain_state
            }
            if self.tower_lat and self.tower_lon:
              self.lastcfg['tower_lat'] = self.tower_lat
              self.lastcfg['tower_lon'] = self.tower_lon

            yaml.dump(self.lastcfg, stream)
