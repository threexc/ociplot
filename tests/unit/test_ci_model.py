import unittest
import numpy as np

from walksignal.models import CIModel, pl_ci

class TestABGModel(unittest.TestCase):
    def test_min_input(self):
        model = CIModel(freq=1, pl_exp=1, sigma=0, ref_dist=1)
        pl = model.path_loss(1)
        self.assertEqual(pl, -27.55)

    def test_one_mhz_one_km(self):
        model = CIModel(freq=1000000, pl_exp=1, sigma=0, ref_dist=1)
        pl = model.path_loss(1000)
        self.assertEqual(pl, 122.45)

if __name__ == '__main__':
    unittest.main()

