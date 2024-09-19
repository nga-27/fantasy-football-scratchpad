#!/usr/bin/env python
# Based on: https://github.com/kennethreitz/setup.py/blob/master/setup.py
"""
Setup tools
Use setuptools to install package dependencies. Instead of a requirements file you
can install directly from this file.
`pip install .`
You can install dev dependencies by targetting the appropriate key in extras_require
```
pip install .[dev] # install requires and test requires
pip install '.[dev]' # install for MAC OS / zsh

```
See: https://packaging.python.org/tutorials/installing-packages/#installing-setuptools-extras
"""
from setuptools import find_packages, setup

# Package meta-data.
NAME = 'fantasy-football-scratchpad'
DESCRIPTION = 'Utilizing some ESPN fantasy football APIs to help manage a league or two simultaneously.'
URL = 'https://github.mmm.com/nga-27/fantasy-football-scratchpad'
EMAIL = 'namell91@gmail.com'
AUTHOR = 'Nick Amell'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = '0.6.4'

# What packages are required for this module to be executed?
REQUIRES = [
    "python-dotenv",
    "numpy==2.1.0",#1.20.2",
    "pandas==2.2.2",#1.2.4",
    "requests==2.32.3",#2.25",
    "xlrd==1.2.0",
    "XlsxWriter==3.2.0",#1.2.6",
    "openpyxl==3.1.5",
    "espn-api==0.38.1",#0.31.0",
    "argparse==1.4.0"
]

REQUIRES_DEV = [
    'colorama==0.4.3',
    'pylint==2.15.2',
    'pycodestyle==2.6.0',
    'pylint-fail-under==0.3.0',
]

REQUIRES_EXE = [
    'pyinstaller==6.10.0'
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=[
            "*.tests",
            "*.tests.*"
            "tests.*",
            "tests"
        ]
    ),
    install_requires=REQUIRES,
    extras_require={
        'dev': REQUIRES_DEV,
        'exe': REQUIRES_EXE
    },
    include_package_data=True,
    license='UNLICENSED',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
