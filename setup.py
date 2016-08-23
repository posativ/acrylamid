#!/usr/bin/env python

import sys
import re

from os.path import join, dirname
from setuptools import setup, find_packages

requires = ['Jinja2>=2.4', 'Markdown>=2.0.1', 'unidecode>=0.04.13']

if sys.version_info < (2, 7):
    requires += ['argparse', 'ordereddict']

if sys.platform == 'win32':
    requires.append('colorama')

setup(
    name='acrylamid',
    version='0.8.dev0',
    author='Martin Zimmermann',
    author_email='info@posativ.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='http://posativ.org/acrylamid/',
    license='BSD revised',
    description='static blog compiler with incremental updates',
    long_description=open(join(dirname(__file__), 'README.rst'), encoding='UTF-8').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ],
    install_requires=requires,
    extras_require={
        'full': ['pygments', 'docutils>=0.9', 'smartypants', 'asciimathml',
                 'textile', 'PyYAML', 'twitter', 'discount'],
        'mako': ['mako>=0.7'],
    },
    tests_require=['Attest-latest', 'cram', 'docutils'],
    test_loader='attest:auto_reporter.test_loader',
    test_suite='specs.testsuite',
    entry_points={
        'console_scripts':
            ['acrylamid = acrylamid:Acryl']
    }
)
