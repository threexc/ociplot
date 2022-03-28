import numpy as np
from PyQt5 import QtGui, QtCore
from pyqtgraph import PlotWidget, mkPen, LegendItem

class PLWidget(PlotWidget):
    def __init__(self, engine, lines):
        super(PLWidget, self).__init__()
        self.styles = {'color':'b', 'font-size':'18px'}
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.5)
        self.setYRange(-150, 150)
        self.setLabel('left', "Path Loss (dB)", **self.styles)
        self.setLabel('bottom', "Distance (m)", **self.styles)
        self.getAxis('left').setTextPen('black')
        self.getAxis('bottom').setTextPen('black')
        self.getAxis('left').setStyle(tickFont=QtGui.QFont('Arial', 12))
        self.getAxis('bottom').setStyle(tickFont=QtGui.QFont('Arial', 12))

        # default plot values
        self.x_range = np.arange(0.5, 2500, 2)
        self.y_range = [randint(0,100) for _ in self.x_range]

        self.engine = engine
        self.lines = lines
        self.pens = {}

        self.setup()

    def setup(self):
        self._initPens()
        self._initLines()

        self.setTitle()

    def _initPens(self):
        self.pens['red'] = mkPen(color=(255, 0, 0), width = 1)
        self.pens['green'] = mkPen(color=(64, 192, 64), width=1)
        self.pens['blue'] = mkPen(color=(0, 0, 255), width=1)
        self.pens['solid'] = mkPen(color=(0, 0, 0), width=3, style=QtCore.Qt.SolidLine)
        self.pens['dot'] = mkPen(color=(255, 144, 0), width=3, style=QtCore.Qt.DotLine)
        self.pens['dash'] = mkPen(color=(128, 64, 64), width=3, style=QtCore.Qt.DashLine)
        self.pens['dashdot'] = mkPen(color=(192,64,192), width=3, style=QtCore.Qt.DashDotLine)
        self.pens['dashdotdot'] = mkPen(color=(64, 64, 144), width=3, style=QtCore.Qt.DashDotDotLine)

    def _initLines(self):
        self.lines['fs'] = self.plot(self.x_range, self.y_range,
                pen=self.pens['solid'], name="Free Space Model")
        self.lines['tworay'] = self.plot(self.x_range, self.y_range,
                pen=self.pens['dot'], name="TwoRay Model")
        self.lines['abg'] = self.plot(self.x_range, self.y_range,
                pen=self.pens['blue'], name="ABG Model")
        self.lines['ci'] = self.plot(self.x_range, self.y_range,
                pen=self.lines['green'], name="CI Model")
        self.lines['ohu'] = self.plot(self.x_range, self.y_range,
                pen=self.pens['dash'], name="Okumura-Hata Urban")
        self.lines['ohs'] = self.plot(self.x_range, self.y_range,
                pen=self.pens['dashdot'], name="Okumura-Hata Suburban")
        self.lines['ohr'] = self.plot(self.x_range, self.y_range,
                pen=self.lines['dashdotdot'], name="Okumura-Hata Rural")
        self.lines['measured'] = self.plot(self.x_range, self.y_range,
                pen=None, symbol="o", symbolPen=self.pens['red'], symbolSize=4, symbolBrush=(255, 0, 0, 255), name="Measured")

    def setTitle(self):
        super.setTitle(f"<p \
                style=\"color:black;font-size:18px\">Path Loss for Cell \
                {self.config.cellid} vs Distance \
                ({self.config.tower_lat},{self.config.tower_lon}), \
                {freq} MHz, G<sub>TX</sub> \
                = {self.config.tx_gain} dB, G<sub>RX</sub> = \
                {self.config.rx_gain} dB</p>")

    def setXScale(self, distances):
        self.setXRange(0, max(distances) + 50)

    def setYScale(self, path_loss, plot_as_gain):
        if plot_as_gain:
            y_min = max(path_loss) * -1 - 20
            y_max = min(path_loss) * -1 + 20
        else:
            y_min = min(path_loss) - 20
            y_max = max(path_loss) + 20

        self.setYRange(y_min, y_max)

    def _updateLegend(self):
        for item in self.plotItem.childItems():
            if isinstance(item, LegendItem):
                self.plotItem.scene().removeItem(item)
        
        legend = LegendItem(offset=(300,210))
        legend.setBrush("#E3E3E3FF")
        legend.setLabelTextColor("#00000000")
        legend.setLabelTextSize("12pt")
        for line in self.lines:
            legend.addItem(line)

        legend.setParentItem(self.plotItem)

    def update(self, distances, cell, path_gain=False):
        if path_gain:
            self.lines['fs'].setData(self.x_range, self.engine.fs_pg_array(self.x_range))
            self.lines['tworay'].setData(self.x_range, self.engine.tworay_pg_array(self.x_range))
            self.lines['ci'].setData(self.x_range, self.engine.ci_pg_array(self.x_range))
            self.lines['abg'].setData(self.x_range, self.engine.abg_pg_array(self.x_range))
            self.lines['ohu'].setData(self.x_range, self.engine.ohu_pg_array(self.x_range))
            self.lines['ohs'].setData(self.x_range, self.engine.ohs_pg_array(self.x_range))
            self.lines['ohr'].setData(self.x_range, self.engine.ohr_pg_array(self.x_range))
            self.lines['measured'].setData(distances, [element * -1 for element in cell.pathloss])
            self.setLabel('left', "Path Gain (dB)", **self.styles)
        else:
            self.lines['fs'].setData(self.x_range, self.engine.fs_pl_array(self.x_range))
            self.lines['tworay'].setData(self.x_range, self.engine.tworay_pl_array(self.x_range))
            self.lines['ci'].setData(self.x_range, self.engine.ci_pl_array(self.x_range))
            self.lines['abg'].setData(self.x_range, self.engine.abg_pl_array(self.x_range))
            self.lines['ohu'].setData(self.x_range, self.engine.ohu_pl_array(self.x_range))
            self.lines['ohs'].setData(self.x_range, self.engine.ohs_pl_array(self.x_range))
            self.lines['ohr'].setData(self.x_range, self.engine.ohr_pl_array(self.x_range))
            self.lines['measured'].setData(distances, cell.pathloss)
            self.setLabel('left', "Path Loss (dB)", **self.styles)

        self._updateLegend()

class PLLine:
    def __init__(self, x_range, y_range, name, pen):
        self.x = x_range
        self.y = y_range
        self.name = name
        self.pen = pen
