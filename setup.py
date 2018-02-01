#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012-2018 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import runpy
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

metadata_filename = "harvest/metadata.py"
metadata = runpy.run_path(metadata_filename)

# http://pypi.python.org/pypi?:action=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "License :: OSI Approved :: Apache Software License",
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
