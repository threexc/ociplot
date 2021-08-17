import unittest
import numpy as np

from walksignal.models import CIModel, pl_ci

class TestABGModel(unittest.TestCase):
    def test_min_input(self):
        model = CIModel(freq=1, pl_exp=1, sigma=0, ref_dist=1)
        pl = model.path_loss(1)
        expected = pl_ci(1, 1, 0, 1, 1)
        self.assertEqual(pl, -90.0)
        self.assertEqual(pl, expected)

    def test_one_mhz_one_km(self):
        model = CIModel(freq=1000000, pl_exp=1, sigma=0, ref_dist=1)
        pl = model.path_loss(1000)
        expected = pl_ci(1000, 1000000, 0, 1, 1)
        self.assertEqual(pl, 0)
        self.assertEqual(pl, expected)

if __name__ == '__main__':
    unittest.main()

