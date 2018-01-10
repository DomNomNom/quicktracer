import threading
from subprocess import Popen, PIPE, TimeoutExpired
import math
import time
import os
import sys
import inspect
import re
import atexit

from .constants import KEY, VALUE, TIME, GUI_COMMAND

bars = None  # initialized in ensureInit
fig = None
ax = None

child_process = None

start_time = time.time()

def trace(value):
    ''' makes a trace chart '''
    start_gui_subprocess()
    frame = inspect.currentframe()
    frame = inspect.getouterframes(frame)[1]
    key = inspect.getframeinfo(frame[0]).code_context[0].strip()
    match = re.search(r'trace\((.*)\)', key)
    if match:
        key = match.group(1)


    data = {
        KEY: key,
        VALUE: value,
        TIME: time.time()-start_time,
    }
    line = repr(data) + '\n'
    message = line.encode('utf-8')
    try:
        child_process.stdin.write(message)
        child_process.stdin.flush()
    except Exception as e:
        raise Exception("tracer GUI died")


def print_file(f):
    for line in f: print(line.decode('utf-8').rstrip())


def start_gui_subprocess():
    # Create a new process such that TKinter doesn't complain about not being in the main thread
    global child_process
    global read_out
    global read_err
    if not child_process:
        quicktracer_dir = os.path.dirname(os.path.realpath(__file__))
        child_process = Popen(GUI_COMMAND, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=quicktracer_dir)
        atexit.register(lambda: child_process.kill())  # behave like a daemon
        read_out = threading.Thread(target=print_file, args=[child_process.stdout], daemon=True)
        read_out.start()
        read_err = threading.Thread(target=print_file, args=[child_process.stderr], daemon=True)
        read_err.start()

def main():
    # Demo: Trace some dummy data
    for i in range(2000):
        trace(30 * math.sin(i/30))
        trace(.3 * math.cos(i/20))
        time.sleep(0.002)


if __name__ == '__main__':
    main()
