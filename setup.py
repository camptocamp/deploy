#!/usr/bin/env python

from distutils.core import setup
from glob import glob

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
]

setup(name = 'deploy',
      version = '0.3',
      url = 'http://www.camptocamp.com/',
      description = 'the c2c project deploy scripts',
      author = 'Camptocamp SA',
      author_email = 'frederic.junod@camptocamp.com',
      packages = ['deploy'],
      scripts = ['bin/deploy'],
      zip_safe = False,
      classifiers = classifiers,
      data_files = [('/etc/deploy/', glob('config/*.cfg')),
                    ('/etc/deploy/hooks/', glob('config/hooks/*')),
                    ('/etc/deploy/hooks-database/', glob('config/hooks-database/*')),
                    ('/etc/deploy/hooks-wms/', glob('config/hooks-wms/*')),
                    ('/etc/deploy/hooks-cw3/', glob('config/hooks-cw3/*'))]
)
