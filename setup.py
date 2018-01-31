#!/usr/bin/env python3

from setuptools import setup
import sys

if sys.version_info < (3,0):
	sys.exit ("Python version < 3.0 is not supported")
elif sys.version_info < (3,6):
	print ("Using Python version < 3.6 would cause issue relevant to the order of windows generated")

setup (name = 'console_ui',
			version = '1.0',
			py_modules=['wingen', 'console_utils'],
      description = 'A quick UI generator using Curses',
      author = 'Hanh Ha',
      author_email = 'tranhanh.haminh@gmail.com',
      license = 'MIT',
			url = 'https://github.com/hanhha/console_ui',
    )
