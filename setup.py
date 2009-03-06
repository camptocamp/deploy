#!/usr/bin/env python

from glob import glob

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

setup(name = 'deploy',
      version = '0.1',
      description = 'the c2c project deploy scripts',
      author = 'Camptocamp SA',
      packages = ['deploy'],
      scripts = ['deploy.py'],
      zip_safe = False,
      classifiers = classifiers,
      data_files = [('/etc', ['deploy.cfg']),
                    ('/etc/deploy/hooks', glob('hooks/*'))]
)



