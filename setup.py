#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

from opps import ganalytics

install_requires = ["opps", "django-celery", "google-api-python-client"]

classifiers = ["Development Status :: 4 - Beta",
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
except:
    long_description = ganalytics.__description__

setup(
    name='opps-ganalytics',
    namespace_packages=['opps', 'opps.ganalytics'],
    version=ganalytics.__version__,
    description=ganalytics.__description__,
    long_description=long_description,
    classifiers=classifiers,
    keywords='google analytics top read',
    author=ganalytics.__author__,
    author_email=ganalytics.__email__,
    packages=find_packages(exclude=('doc', 'docs',)),
    install_requires=install_requires,
    include_package_data=True
)
