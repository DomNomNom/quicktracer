# -*- coding: utf-8 -*-

'''
GUI for quicktracer
'''


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from collections import deque
import sys
import threading
import json
import os

from constants import KEY, VALUE, TIME

MAX_DATA_SERIES_LENGTH = 1000
ANIMATION_UPDATE_INTERVAL = 10 # ms

# Globals
key_to_plot = {}

num_plots_in_window = 0
def new_row_id():
    global num_plots_in_window
    num_plots_in_window += 1
    return num_plots_in_window

# TODO: inheritance maybe
class TimeseriesPlot(object):
    def __init__(self, title):
        self.title = title
        self.value_data = deque([], maxlen=MAX_DATA_SERIES_LENGTH)
        self.time_data = deque([], maxlen=MAX_DATA_SERIES_LENGTH)
        self.plot = None
        self.curve = None

    def add_value(self, message):
        self.time_data.append(message[TIME])
        self.value_data.append(message[VALUE])

    def render(self, win):
        if not self.plot:
            self.plot = win.addPlot(title=self.title, row=new_row_id(), col=0)
            self.plot.showAxis('left', False)
            self.plot.showAxis('right', True)
            self.curve = self.plot.plot()
        self.curve.setData(self.time_data, self.value_data)

class XYPlot(object):
    def __init__(self, title):
        self.title = title
        self.x_data = deque([], maxlen=MAX_DATA_SERIES_LENGTH)
        self.y_data = deque([], maxlen=MAX_DATA_SERIES_LENGTH)
        self.plot = None
        self.curve = None
        self.curve_point = None

    def add_value(self, message):
        vector = message[VALUE]
        assert is_vector2(vector)
        self.x_data.append(vector[0])
        self.y_data.append(vector[1])

    def render(self, win):
        if not self.plot:
            self.plot = win.addPlot(title=self.title, row=new_row_id(), col=0)
            self.curve = self.plot.plot()
            self.curve.setData(self.x_data, self.y_data)
            self.curve_point = pg.CurvePoint(self.curve)
            self.plot.addItem(self.curve_point)
            self.point_label = pg.TextItem('[?, ?]', anchor=(0.5, -1.0))
            self.point_label.setParentItem(self.curve_point)
            arrow2 = pg.ArrowItem(angle=90)
            arrow2.setParentItem(self.curve_point)
        self.curve.setData(self.x_data, self.y_data)
        self.curve_point.setIndex(0)  # Force a redraw if if the length doesn't change
        index = len(self.x_data)-1
        self.curve_point.setIndex(index)
        self.point_label.setText('[%0.1f, %0.1f]' % (self.x_data[index], self.y_data[index]))





def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False
def is_vector2(vector):
    try:
        assert len(vector) == 2
        assert is_number(vector[0])
        assert is_number(vector[1])
        return True
    except Exception:
        return False


def read_input():
    global key_to_plot
    try:
        while True:
            try:
                line = input()
            except EOFError as e:
                return
            message = json.loads(line)
            key = message[KEY]
            if key not in key_to_plot:
                create_plot(message)
            key_to_plot[key].add_value(message)
    except Exception as e:
        print()
        print('ERROR:')
        print(e)
        print()
        sys.stdout.flush()
        os.exit(-1)

def create_plot(message):
    global key_to_plot
    key = message[KEY]
    value = message[VALUE]
    if is_number(value): plot = TimeseriesPlot(title=key)
    elif is_vector2(value): plot = XYPlot(title=key)
    else: raise Exception('unexpected datatype. key={} value={}: '.format(key, repr(value)))
    key_to_plot[key] = plot
    return plot


class NonFocusStealingGraphicsWindow(pg.GraphicsWindow):
    def show(self):
        self.setAttribute(98) # Qt::WA_ShowWithoutActivating
        super().show()



def main():
    app = QtGui.QApplication([])
    win = NonFocusStealingGraphicsWindow(title='quicktracer')
    win.setGeometry(0, 50, 500, 500)

    threading.Thread(target=read_input, daemon=True).start()

    def update():
        global key_to_plot
        try:
            for key in sorted(key_to_plot):
                key_to_plot[key].render(win)
        except Exception as e:
            print(e)
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
