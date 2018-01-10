import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
from ast import literal_eval
import os
import sys
import time

from constants import KEY, VALUE, TIME

MAX_DATA_SERIES_LENGTH = 1000
ANIMATION_UPDATE_INTERVAL = 10 # ms

# global variables (bad)
key_to_series = {}  # [ bob: {TIME: [t,t,t,t], VALUE: [v,v,v,v] }]
key_to_plot = {}
fig = None
axes = []
keys = []  # parallel to axes

def animate(frameno):
    global axes
    if not axes: return axes

    for key in key_to_plot:
        plot = key_to_plot[key]
        plot.set_data(
            key_to_series[key][TIME],
            key_to_series[key][VALUE],
        )

    min_time = min(min(key_to_series[key][TIME]) for key in keys)
    max_time = max(max(key_to_series[key][TIME]) for key in keys)
    if min_time == max_time:
        min_time -= 1
    for ax, key in zip(axes, keys):
        min_val = min(key_to_series[key][VALUE])
        max_val = max(key_to_series[key][VALUE])
        padding = (max_val - min_val) * 0.1
        ax.set_ylim(
            min_val - padding,
            max_val + padding
        )
        ax.set_xlim(min_time, max_time)

    return axes



def start_gui():
    global fig
    global axes
    plt.style.use('dark_background')
    fig = plt.figure(
        # figsize=(6, 8),
        )
    time.sleep(1)
    # create_plot().plot([1,4,3])
    # create_plot().plot([-1,-4,-3])
    anim = animation.FuncAnimation(fig, animate, interval=ANIMATION_UPDATE_INTERVAL)
    fig.tight_layout()
    plt.show()

def create_plot(key):
    global fig
    global axes
    # Now later you get a new subplot; change the geometry of the existing
    n = len(axes)
    for i in range(n):
        axes[i].change_geometry(n+1, 1, i+1)

    # Add the new
    ax = fig.add_subplot(n+1, 1, n+1)
    ax.set_title(key)
    axes.append(ax)
    keys.append(key)
    plot, = ax.plot([1], [2])
    plt.tick_params(
        axis='x',
        which='both',
        bottom='on',
        top='off',
        labelbottom='off',
        direction='in',
    )

    key_to_series[key] = {TIME: [], VALUE: []}
    key_to_plot[key] = plot

def downsample(series):
    return series[-MAX_DATA_SERIES_LENGTH:]
    # if len(series) < MAX_DATA_SERIES_LENGTH:
    #     return series
    # half = len(series) // 2
    # return series[:half:2] + series[half:]


def read_input():
    global key_to_series
    global fig
    try:
        while True:
            try:
                line = input()
            except EOFError as e:
                return
            if not fig:
                continue
            line = literal_eval(line)
            key = line[KEY]
            if key not in key_to_series:
                create_plot(key)
            key_to_series[key][TIME].append(line[TIME])
            key_to_series[key][VALUE].append(line[VALUE])
            key_to_series[key][TIME] = downsample(key_to_series[key][TIME])
            key_to_series[key][VALUE] = downsample(key_to_series[key][VALUE])
    except Exception as e:
        print()
        print('ERROR:')
        print(e)
        print()
        sys.stdout.flush()
        os.exit(-1)


def main():
    threading.Thread(target=read_input, daemon=True).start()
    start_gui()


if __name__ == '__main__':
    main()
