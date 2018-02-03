import math
import time
from quicktracer import trace

def main():

    # Trace some dummy data
    for i in range(120*60):
        # Demo: Simple and common usecase
        trace(30 * math.sin(i/30))

        # Demo: Vector display and having multiple displays in one view_box
        t = i / 100
        t += math.sin(t)
        trace([math.cos(t) * 2, math.cos(20*t)], view_box='Wave-like things')
        trace([math.cos(t) + 5, math.sin(t)   ], view_box='Wave-like things')

        # Custom display
        trace(almost_fizzbuzz(i), custom_display=StringCounter)

        time.sleep(1/60.)  # Simulate an external main loop



def almost_fizzbuzz(i):
    out = ''
    if i%3 == 0: out += 'Fizz'
    if i%5 == 0: out += 'Buzz'
    if out == '':
        out = '(neither)'
    return out

# These imports down here as you'll only need them when you implement your own Display.
from quicktracer import Display, VALUE
from collections import Counter
import pyqtgraph as pg

class StringCounter(Display):
    def __init__(self):
        super().__init__()
        self.counts = Counter()
        self.bar_width = 0.3
        self.bar_graph = pg.BarGraphItem(x0=[1], height=[1], width=self.bar_width, brush='r')
        self.stringaxis = pg.AxisItem(orientation='bottom')
    @classmethod
    def accepts_value(cls, value):
        return type(value) is str
    def add_value(self, message):
        value = message[VALUE]
        self.counts[value] += 1
    def init_view_box(self, view_box):
        view_box.addItem(self.bar_graph)
        def my_tick_strings(values, scale, spacing):
            keys = sorted(self.counts.keys())
            return [keys [int(round(value))] if 0 <= round(value) < len(keys) else '' for value in values]
        view_box.axes['bottom']['item'].tickStrings = my_tick_strings
    def render(self):
        keys = sorted(self.counts.keys())
        self.stringaxis.setTicks(keys)
        values = [ self.counts[key] for key in keys ]
        x0 = [ i-0.5*self.bar_width for i in range(len(keys)) ]
        self.bar_graph.setOpts(x0=x0, height=values, width=self.bar_width)


if __name__ == '__main__':
    main()

