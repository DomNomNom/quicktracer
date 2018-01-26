
def main():
    import math
    import time
    from quicktracer import trace

    # Demo: Trace some dummy data
    for i in range(40*60):
        # Simple and common usecase
        trace(30 * math.sin(i/30))

        # Vectors are supported
        t = i / 100
        t += math.sin(t)
        trace([math.cos(t), math.cos(30*t)])

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

from quicktracer import Display, VALUE
from collections import Counter
import pyqtgraph as pg

class StringCounter(Display):
    def __init__(self):
        super().__init__()
        self.counts = Counter()
        self.bar_graph = pg.BarGraphItem(x0=[1], height=[1], width=0.3, brush='r')
        self.stringaxis = pg.AxisItem(orientation='bottom')
    @classmethod
    def accepts_value(cls, value):
        return type(value) is str
    def add_value(self, message):
        value = message[VALUE]
        self.counts[value] += 1
    def init_view_area(self, view_area):
        view_area.addItem(self.bar_graph)
        def my_tick_strings(values, scale, spacing):
            keys = sorted(self.counts.keys())
            return [keys [int(value)] if 0 <= int(value) < len(keys) else '' for value in values]
        view_area.axes['bottom']['item'].tickStrings = my_tick_strings
    def render(self):
        keys = sorted(self.counts.keys())
        self.stringaxis.setTicks(keys)
        values = [ self.counts[key] for key in keys ]
        width = 0.3
        x0 = [ i-0.5*width for i in range(len(keys)) ]
        self.bar_graph.setOpts(x0=x0, height=values, width=0.3)


if __name__ == '__main__':
    main()

