from collections import deque
import pyqtgraph as pg

# Protocol constants (duplicated because of import problems)
KEY = 'k'
VALUE = 'v'
TIME = 't'
CUSTOM_DISPLAY = 'custom_display'

DEFAULT_MAX_DATA_SERIES_LENGTH = 1000

view_boxes = {}

class Display():
    # Override these
    def __init__(self):
        self.title = None
        self.view_area = None
        self.view_box_id = None
    @classmethod
    def accepts_value(cls, value):
        return True
    def add_value(self, message):
        pass
    def init_view_area(self, view_area):
        pass
    def render(self):
        pass

    # Shouldn't need to override these ones
    def render_with_init(self, win):
        if not self.view_area:
            global view_boxes
            if self.view_box_id:
                if self.view_box_id in view_boxes:
                    self.view_area = view_boxes[self.view_box_id]
                    self.view_area.setTitle('')
                else:
                    win.nextRow()
                    self.view_area = win.addPlot(title=self.title)
                    view_boxes[self.view_box_id] = self.view_area
            else:
                win.nextRow()
                self.view_area = win.addPlot(title=self.title)
            self.init_view_area(self.view_area)
        self.render()
    def set_title(self, title):
        self.title = title
    def set_view_box_id(self, view_box_id):
        self.view_box_id = view_box_id


# Built-in stuff below.

num_plots_in_window = 0
def new_row_id():
    global num_plots_in_window
    print('aa', num_plots_in_window)
    num_plots_in_window += 1
    return num_plots_in_window


class TimeseriesPlot(Display):
    def __init__(self):
        super().__init__()
        self.value_data = deque([], maxlen=DEFAULT_MAX_DATA_SERIES_LENGTH)
        self.time_data = deque([], maxlen=DEFAULT_MAX_DATA_SERIES_LENGTH)
    @classmethod
    def accepts_value(cls, value):
        return is_number(value)

    def add_value(self, message):
        self.time_data.append(message[TIME])
        self.value_data.append(float(message[VALUE]))
        self.title = message[KEY]

    def init_view_area(self, view_area):
        view_area.showAxis('left', False)
        view_area.showAxis('right', True)
        self.curve = view_area.plot()
    def render(self):
        self.curve.setData(self.time_data, self.value_data)

class XYPlot(Display):
    def __init__(self):
        super().__init__()
        self.x_data = deque([], maxlen=DEFAULT_MAX_DATA_SERIES_LENGTH)
        self.y_data = deque([], maxlen=DEFAULT_MAX_DATA_SERIES_LENGTH)
        self.vector_data = deque([], maxlen=DEFAULT_MAX_DATA_SERIES_LENGTH)
        self.curve = None
        self.curve_point = None
    @classmethod
    def accepts_value(cls, value):
        return is_vector(value)

    def add_value(self, message):
        vector = message[VALUE]
        assert is_vector(vector)
        self.title = message[KEY]
        self.x_data.append(vector[0])
        self.y_data.append(vector[1])
        self.vector_data.append(vector)

    def init_view_area(self, view_area):
        self.curve = view_area.plot()
        self.curve.setData(self.x_data, self.y_data)
        self.curve_point = pg.CurvePoint(self.curve)
        view_area.addItem(self.curve_point)
        self.point_label = pg.TextItem('[?, ?]', anchor=(0.5, -1.0))
        self.point_label.setParentItem(self.curve_point)
        arrow2 = pg.ArrowItem(angle=90)
        arrow2.setParentItem(self.curve_point)

    def render(self):
        index = min(len(self.x_data), len(self.y_data))-1
        self.curve.setData(self.x_data, self.y_data)
        self.curve_point.setIndex(0)  # Force a redraw if if the length doesn't change
        self.curve_point.setIndex(index)
        self.point_label.setText('[{}]'.format(
            ', '.join([ '{:0.1f}'.format(val) for val in self.vector_data[index] ])
        ))

def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False
def is_vector(vector):
    try:
        assert len(vector) >= 2
        assert is_number(vector[0])
        assert is_number(vector[1])
        return True
    except Exception:
        return False

default_display_classes = [
    TimeseriesPlot,
    XYPlot,
]
