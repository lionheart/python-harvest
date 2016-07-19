#!/usr/bin/env python

import os
from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

metadata = {}
execfile("harvest/metadata.py", metadata)

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries",
    "Topic :: Internet :: WWW/HTTP :: Site Management",
    "Topic :: Utilities",
    "License :: OSI Approved :: MIT License",
]

setup(
    name='python-harvest-redux',
    version=metadata['__version__'],
    description="Harvest API client",
    long_description="Harvest Time Tracking API Client",
    classifiers=classifiers,
    keywords='harvestapp timetracking api',
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    url='https://github.com/lionheart/python-harvest',
    license=metadata['__license__'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=read("requirements.txt").split("\n")
)
