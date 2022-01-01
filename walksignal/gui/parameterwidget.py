import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import pandas as pd

class ParameterWidget(QtWidgets.QWidget):

    """ ParameterWidget is a composite widget that provides an
    interconnected slider and text box with naming and label display.
    The scale value is to account for conversion of the integer value of
    the slider into a floating point value to be used with the textbox
    and any external tools. slider_event_func and text_event_func are
    the external methods that the widgets must be connected to in
    addition to their mutual update functions setValueFromText and
    setValueFromSlider."""
    def __init__(self, name, unit, value = 0, min_value = 0, max_value = 100, scale = 10, slider_event_func = None, text_event_func = None):
        super(ParameterWidget, self).__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.scale = scale
        self.box_width = 40
        self.parameter_label = QtWidgets.QLabel(name)
        self.unit_label = QtWidgets.QLabel(unit)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(self.min_value, self.max_value)
        self.slider.setValue(int(self.value * self.scale))
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider.valueChanged[int].connect(slider_event_func)
        self.slider.valueChanged[int].connect(self.setValueFromSlider)

        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.setFixedWidth(self.box_width)
        self.textbox.setText(str(self.value))
        self.textbox.textChanged.connect(text_event_func)
        self.textbox.editingFinished.connect(self.setValueFromText)

        self.layout.addWidget(self.parameter_label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.unit_label)
        self.setLayout(self.layout)

    def setValueFromText(self):
        if self.textbox.text():
            self.value = float(self.textbox.text() or 0)
            self.slider.setValue(int(self.value * self.scale))

    def setValueFromSlider(self):
        self.value = float(self.slider.value() or 0) / self.scale
        self.textbox.setText(str(self.value))
