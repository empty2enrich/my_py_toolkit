#!/usr/bin/env python
import os
from fdfs_client import __version__
try:
    from setuptools import setup, Extension
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
    'packages' : ['my_py_toolkit'],
    'classifiers' : [
        'Development Status :: 1 - Production/Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: GPLV3',
        'Operating System :: OS Independent',
        'Programming Language :: Python']
}


setup(**sdict)
