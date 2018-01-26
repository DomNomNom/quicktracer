import threading
from subprocess import Popen, PIPE
import math
import time
import os
import sys
import inspect
import re
import atexit
import collections
import json


# Protocol constants
KEY = 'k'
VALUE = 'v'
TIME = 't'
CUSTOM_DISPLAY = 'custom_display'



GUI_COMMAND = 'python gui_pyqtgraph.py'
child_process = None
have_notified_about_child_dying = False

start_time = time.time()

last_modification_times = {}  # parent source filepath -> time

def trace(value, key=None, custom_display=None, reset_on_parent_change=True):
    '''
        Makes a trace chart.

        Arguments:
            value:
                The thing to trace.
                Can be a number.
                TODO: allow 2d vectors
                TODO: allow 3d vectors
            key:
                The identifier keeping the value unique
                Optional string
            custom_display:
                A class inheriting from quicktracer.Display
            reset_on_parent_change:
                whether we should restart the trace if the caller has chagned the file.
     '''

    if reset_on_parent_change:
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        parent_path = inspect.getframeinfo(frame[0]).filename

        new_modification_time = os.stat(parent_path).st_mtime
        if new_modification_time != last_modification_times.get(parent_path, 0):
            last_modification_times[parent_path] = new_modification_time
            reset()

    start_gui_subprocess()
    if key is None:
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        key = inspect.getframeinfo(frame[0]).code_context[0].strip()
        match = re.search(r'trace\((.*)\)', key)
        if match:
            key = match.group(1)


    # convert numpy arrays into lists
    if isinstance(value, collections.Iterable) and not isinstance(value, str):
        value = list(value)

    data = {
        KEY: key,
        VALUE: value,
        TIME: time.time()-start_time,
    }

    if custom_display is not None:
        data[CUSTOM_DISPLAY] = [inspect.getfile(custom_display), custom_display.__name__]
    line = json.dumps(data) + '\n'
    message = line.encode('utf-8')
    try:
        child_process.stdin.write(message)
        child_process.stdin.flush()
    except Exception as e:
        global have_notified_about_child_dying
        if have_notified_about_child_dying:
            return
        have_notified_about_child_dying = True
        raise Exception("=== quicktracer GUI died ===")


def print_file(f):
    for line in f: print(line.decode('utf-8').rstrip())

def reset():
    global child_process
    if child_process:
        child_process.kill()
        child_process = None
        # start_gui_subprocess()

def start_gui_subprocess():
    # Create a new process such that TKinter doesn't complain about not being in the main thread
    global child_process
    global read_out
    global read_err
    if not child_process:
        quicktracer_dir = os.path.dirname(os.path.realpath(__file__))

        child_process = Popen(
            GUI_COMMAND,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            cwd=quicktracer_dir,
        )
        atexit.register(lambda: child_process.kill())  # behave like a daemon
        read_out = threading.Thread(target=print_file, args=[child_process.stdout], daemon=True)
        read_out.start()
        read_err = threading.Thread(target=print_file, args=[child_process.stderr], daemon=True)
        read_err.start()

if __name__ == '__main__':
    main()
