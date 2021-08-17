import unittest

from walksignal.models import ABGModel, pl_abg

class TestABGModel(unittest.TestCase):
    def test_min_input(self):
        model = ABGModel(freq=1, alpha=1, beta=0, gamma=1, sigma=0)
        pl = model.path_loss(1)
        expected = pl_abg(1, 1, 1, 0, 1, 0)
        self.assertEqual(pl, -90.0)
        self.assertEqual(pl, expected)

    def test_one_mhz_one_km(self):
        model = ABGModel(freq=1000000, alpha=1, beta=0, gamma=1, sigma=0)
        pl = model.path_loss(1000)
        expected = pl_abg(1000, 1000000, 1, 0, 1, 0)
        self.assertEqual(pl, 0)
        self.assertEqual(pl, expected)

if __name__ == '__main__':
    unittest.main()

