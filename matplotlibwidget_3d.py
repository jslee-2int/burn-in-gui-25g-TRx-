# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License

"""
MatplotlibWidget
================
Example of matplotlib widget for PyQt4
Copyright © 2009 Pierre Raybaut
This software is licensed under the terms of the MIT License
Derived from 'embedding_in_pyqt4.py':
Copyright © 2005 Florent Rougon, 2006 Darren Dale
"""

__version__ = "1.0.0"

from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter

from matplotlib import rcParams

rcParams['font.size'] = 9


class MatplotlibWidget_3D(Canvas):
    """
    MatplotlibWidget inherits PyQt4.QtGui.QWidget
    and matplotlib.backend_bases.FigureCanvasBase

    Options: option_name (default_value)
    -------
    parent (None): parent widget
    title (''): figure title
    xlabel (''): X-axis label
    ylabel (''): Y-axis label
    xlim (None): X-axis limits ([min, max])
    ylim (None): Y-axis limits ([min, max])
    xscale ('linear'): X-axis scale
    yscale ('linear'): Y-axis scale
    width (4): width in inches
    height (3): height in inches
    dpi (100): resolution in dpi
    hold (False): if False, figure will be cleared each time plot is called

    Widget attributes:
    -----------------
    figure: instance of matplotlib.figure.Figure
    axes: figure axes

    Example:
    -------
    self.widget = MatplotlibWidget(self, yscale='log', hold=True)
    from numpy import linspace
    x = linspace(-10, 10)
    self.widget.axes.plot(x, x**2)
    self.wdiget.axes.plot(x, x**3)
    """
    data = [[1, 1, 0.34053397, 0.11315148, 1, 1, 0.28831287, 0.68246773],
            [0.53473005, 1, 0.63312686, 1, 0.43377528, 1, 0.78892828, 0.22746536],
            [1, 1, 0.62309026, 1, 1, 0.01694372, 1, 0.78965345],
            [0.91814725, 1, 1, 0.10620847, 1, 0.5832605, 0.32565308, 0.0101006],
            [0.83161979, 1, 0.70209012, 1, 1, 1, 0.78354307, 1]]

    def __init__(self, parent=None, title='', xlabel='', ylabel='',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=4, height=3, dpi=75, hold=False, bg_color='#FFF'):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=bg_color)
        # self.figure.subplots_adjust(right=0.8)
        self.axes = self.figure.subplots(5, 1)
        self.axes[0].get_xaxis().set_visible(False)
        self.axes[1].get_xaxis().set_visible(False)
        self.axes[2].get_xaxis().set_visible(False)
        self.axes[3].get_xaxis().set_visible(False)
        formatter = FuncFormatter(self.format_y_tick)
        # self.axes[0].yaxis.set_major_formatter(formatter)
        # self.axes[1].yaxis.set_major_formatter(formatter)
        self.axes[2].yaxis.set_major_formatter(formatter)
        self.axes[3].yaxis.set_major_formatter(formatter)

        # self.axes[4].yaxis.set_major_formatter(formatter)
        # self.axes.set_title(title)
        # self.axes.set_xlabel(xlabel)
        # self.axes.set_ylabel(ylabel)
        # if xscale is not None:
        #     self.axes.set_xscale(xscale)
        # if yscale is not None:
        #     self.axes.set_yscale(yscale)
        # if xlim is not None:
        #     self.axes.set_xlim(*xlim)
        # if ylim is not None:
        #     self.axes.set_ylim(*ylim)
        # self.axes.hold(hold)

        # self.axes2 = self.axes.twinx()

        Canvas.__init__(self, self.figure)
        self.setParent(parent)

        Canvas.setSizePolicy(self, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        Canvas.updateGeometry(self)

    def format_y_tick(self, value, tick_number):
        return '{:.0f}k'.format(value / 1000)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)


# ===============================================================================
#   Example
# ===============================================================================
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QMainWindow, QApplication
    from numpy import linspace


    class ApplicationWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self.mplwidget = MatplotlibWidget_3D(self, title='Example',
                                              xlabel='Linear scale',
                                              ylabel='Log scale',
                                              hold=True, yscale='log')
            self.mplwidget.setFocus()
            self.setCentralWidget(self.mplwidget)

            self.plot(self.mplwidget.axes)

        def plot(self, axes):
            # x = linspace(-10, 10)
            # plot data on each subplot
            axes[0].bar(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'], [4, 5, 6, 5, 6, 5, 6, 2], color='#FF003C')
            axes[1].bar(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'], [4, 5, 6, 5, 6, 5, 6, 2], color='#FF8A00')
            axes[2].bar(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'], [4, 5, 6, 5, 6, 5, 6, 2], color='#FABE28')
            axes[3].bar(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'], [4, 5, 6, 5, 6, 5, 6, 2], color='#88C100')
            axes[4].bar(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'], [4, 5, 6, 5, 6, 5, 6, 2], color='#00C176')
            # axes[2, 1].plot([1, 2, 3], [4, 5, 6], 'o-')


            # axes[4].get_xaxis().set_visible(False)

            axes[0].set_ylabel("Curr.")
            axes[1].set_ylabel("Temp.")
            axes[2].set_ylabel("MPD")
            axes[3].set_ylabel("RSSI")
            axes[4].set_ylabel("TEC")
            # axes.legend(loc='upper center', bbox_to_anchor=(1.1, 1), ncol=1)


    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    app.exec()