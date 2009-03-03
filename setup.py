#!/usr/bin/env python

import sys

try:
    from setuptools import setup
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
]

# We'd like to let debian install the /etc/deploy.cfg,
# but put them in tilecache/tilecache.cfg using setuptools
# otherwise. 
extra = {}
if "--debian" in sys.argv:
    extra['data_files']=[('/etc', ['deploy.cfg'])]
    sys.argv.remove("--debian")
else:
   extra['data_files']=[('deploy', ['tilecache.cfg'])]

setup(name='deploy',
      version='0.1',
      description='the c2c project deploy scripts',
      author='Camptocamp SA',
      packages=['deploy'],
      scripts=['deploy.py'],
      zip_safe=False,
      classifiers=classifiers, 
      **extra 
)

      
      
