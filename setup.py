#!/usr/bin/python
# -*- coding: utf8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='ibasis',
    version='0.0.2',
    author='Avins Wang',
    author_email='avinswang@gmail.com',
    url='https://github.com/AvinsWang/ibasis',
    download_url="http://pypi.python.org/pypi/ibasis/",
    description="basic functions in coding, include fio, image processing, profile, etc.",
    long_description=open(os.path.join(here, 'README.md')).read(),
    license='LGPL-3.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['py-itime', 'python time'],
    classifiers=['Topic :: Utilities', 
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                 'Programming Language :: Python :: 3.8'],
)