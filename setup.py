#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import find_packages, setup

from opps import ganalytics

install_requires = [i.strip() for i in open("requirements.txt").readlines()]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Framework :: Django",
    'Programming Language :: Python',
    "Programming Language :: Python :: 2.7",
    "Operating System :: OS Independent",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    'Topic :: Software Development :: Libraries :: Python Modules']

try:
    long_description = open('README.md').read()
except IOError:
    long_description = ganalytics.__description__

setup(
    name='opps-ganalytics',
    namespace_packages=['opps'],
    version=ganalytics.__version__,
    description=ganalytics.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    keywords='google analytics top read',
    author=ganalytics.__author__,
    author_email=ganalytics.__email__,
    packages=find_packages(exclude=('doc', 'docs',)),
    install_requires=install_requires,
    package_dir={'opps': 'opps'},
    include_package_data=True
)
