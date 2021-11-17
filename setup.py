#!/usr/bin/env python
import os
__version__ = "0.0.10.8"
try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from distutils.core import setup, Extension

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

sdict = {
    'name' : 'my_py_toolkit',
    'version' : __version__,
    'description' : '',
    'long_description' : long_description,
    'author' : '',
    'author_email' : '',
    'maintainer' : '',
    'maintainer_email' : '',
    'keywords' : [''],
    'license' : 'GPLV3',
    'packages' : find_packages(),
    'install_requires': [

    ],
    'classifiers' : [
        'Development Status :: 1 - Production/Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: GPLV3',
        'Operating System :: OS Independent',
        'Programming Language :: Python']
}


setup(**sdict)
