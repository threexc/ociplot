import yaml
import numpy as np
import pyqtgraph as pg
from random import randint

class Config:
    def __init__(self, filename="lastcfg.yaml"):

        self.filename = filename
        try:
            with open(self.filename) as stream:
                self.data = yaml.safe_load(stream)
                self.signal_data_file = self.data.get("signal_data_file")
                self.bitrate_data_file = self.data.get("bitrate_data_file")
                self.tower_lat = self.data.get("tower_lat")
                self.tower_lon = self.data.get("tower_lon")
        except:
            print("Could not load {0}. Setting defaults...".format(self.filename))

        self.signal_dataset = None
        self.x_range = None
        self.y_range = None
        self.bitrate_dataset = None

        self.cell = None
        self.cell_pl = None
        self.cell_distances = None
        self.tower = None
        self.cbar = None

        self.br_distances = None

        self.pl_points = np.arange(0.5, 2500, 0.5)
        self.pl_freq = 50
        self.pl_alpha = 1
        self.pl_beta = 1
        self.pl_gamma = 1
        self.pl_sigma = 1
        self.pl_exp = 1
        self.pl_exp_tworay = 1
        self.pl_ref_dist = 1
        self.pl_ref_pl = 80
        self.pl_ref_freq = 1000000000
        self.pl_fs_y = None
        self.pl_tx_power = 43
        self.pl_tx_gain = 3
        self.pl_rx_gain = 3
        self.pl_bs_height = 1
        self.pl_ue_height = 1
        self.pl_correction_factor = 1
        self.pl_large_city = True
        self.pl_path_gain = False

        self.pl_green_pen = pg.mkPen(color=(64, 192, 64))
        self.pl_blue_pen = pg.mkPen(color=(0, 0, 255))
        self.pl_green_pen = pg.mkPen(color=(64,192,64))
        self.pl_black_pen = pg.mkPen(color=(0, 0, 0))
        self.pl_orange_pen = pg.mkPen(color=(255, 145, 0))
        self.pl_oh_u_pen = pg.mkPen(color=(0, 255, 0))
        self.pl_oh_s_pen = pg.mkPen(color=(192,64,192))
        self.pl_oh_r_pen = pg.mkPen(color=(64, 64, 144))

        self.styles = {'color':'b', 'font-size':'18px'}
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

    def save(self):
        with open(self.filename, "w") as stream:
            yaml.dump(self.data, stream)

    def set(self, newconfig):
        self.data = newconfig
