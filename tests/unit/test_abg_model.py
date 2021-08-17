import unittest

from walksignal.models import ABGModel, pl_abg

class TestABGModel(unittest.TestCase):
    def test_min_input(self):
        model = ABGModel(freq=1, alpha=1, beta=0, gamma=1, sigma=0)
        pl = model.path_loss(1)
        self.assertEqual(pl, -90.0)

    def test_one_mhz_one_km(self):
        model = ABGModel(freq=1000000, alpha=1, beta=0, gamma=1, sigma=0)
        pl = model.path_loss(1000)
        self.assertEqual(pl, 0)

if __name__ == '__main__':
    unittest.main()

