from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = 'quicktracer',
  packages = ['quicktracer'],
  version = '1.2.0',
  description = 'A simple function to do realtime tracing/monitoring/plotting',
  author = 'DomNomNom',
  author_email = 'dominikschmid93+quicktracer@gmail.com',
  url = 'https://github.com/DomNomNom/quicktracer',
  long_description=read('README'),
  license = "MIT",
  keywords = ['testing', 'tracing', 'plot', 'RLBot', 'quicktracer', 'realtime', 'monitoring'],
  classifiers = [],
  install_requires = [
    'pyqtgraph>=0.10.0',
    'pyqt5',
  ]
)

