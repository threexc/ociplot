import os.path
import matplotlib.pyplot as pyplot

class CellMap:
    """Class containing OpenStreetMap imagery info."""
    def __init__(self, map_path):
        self.map_path = map_path
        self.bbox_path = os.path.dirname(self.map_path) + "/bbox.txt"

    def get_map(self):
        return pyplot.imread(self.map_path)

    def get_bbox(self):
        bbox = None
        with open(self.bbox_path) as f:
            bbox = [tuple(map(float, i.split(','))) for i in f]
        return bbox

