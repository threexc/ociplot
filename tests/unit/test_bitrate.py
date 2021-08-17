import unittest
import os
from walksignal.bitrate import BitRate, BitRateSet

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'sample.txt')

class TestBitRateSet(unittest.TestCase):
    def test_bitrateset_means(self):
        bitrateset = BitRateSet(TESTDATA_FILENAME) 
        points = bitrateset.get_points()
        self.assertAlmostEqual(bitrateset.get_mean("jitter").round(2), 10.42)
        self.assertAlmostEqual(bitrateset.get_mean("down").round(2), 40.27)
        self.assertAlmostEqual(bitrateset.get_mean("up").round(2), 43.32)

if __name__ == '__main__':
    unittest.main()

