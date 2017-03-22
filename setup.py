#!/usr/bin/env python

from distutils.core import setup

setup(
  name = 'diskrec',
  packages = ['diskrec'],
  scripts = [
    'scripts/diskrec_server'
  ],
  classifiers = [
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering'
  ]
)
