import unittest

from walksignal.models import FreeSpaceModel, pl_fs

class TestFreeSpaceModel(unittest.TestCase):
    def test_min_input(self):
        model = FreeSpaceModel(1)
        pl = model.path_loss(1)
        self.assertEqual(pl, -27.55)

    def test_one_mhz_one_km(self):
        model = FreeSpaceModel(1000000)
        pl = model.path_loss(1000)
        self.assertEqual(pl, 152.45)

if __name__ == '__main__':
    unittest.main()

