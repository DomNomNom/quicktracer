from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import mmap
import ctypes
import math

SHARED_MEMORY_TAG = 'Local\\RLBotOutput'
CAR_WIDTH = 300.0
UCONST_Pi = 3.1415926
URotation180 = float(32768)
URotationToRadians = UCONST_Pi / URotation180

class Visualizer(object):
    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 50, 600, 600)
        self.w.setAttribute(98)
        self.w.show()

        # create the background grids
        gx = gl.GLGridItem()
        gx.setSize(12000, 12000, 10000)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-6000, 0, 0)
        gx.setSpacing(100, 100, 100)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -6000, 0)
        gy.setSize(12000, 12000, 10000)
        gy.setSpacing(100, 100, 100)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.setSize(12000, 12000, 10000)
        gz.setSpacing(100, 100, 100)
        self.w.addItem(gz)


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plot_car_data(self):
        pass

    def update(self):
        self.set_plot_car_data()

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer()
    v.animation()

