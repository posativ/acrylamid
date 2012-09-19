#!/usr/bin/env python

import sys
import re

from os.path import join, dirname
from setuptools import setup, find_packages

version = re.search("__version__ = '([^']+)'",
                    open('acrylamid/__init__.py').read()).group(1)

requires = ['Jinja2>=2.4', 'Markdown>=2.0.1']
kw = {}

if sys.version_info[0] >= 3:
    kw["use_2to3"] = True
    kw['use_2to3_exclude_fixers'] = ['lib2to3.fixes.execfile', ]
else:
    requires.append('translitcodec>=0.2')

if sys.version_info < (2, 7):
    requires.append('argparse')

if '--full' in sys.argv:
    requires.extend([
        'pygments',
        'docutils',
        'smartypants',
        'asciimathml',
        'textile',
        'unidecode',
        'PyYAML'
    ])

if '--mako' in sys.argv:
    requires.remove('Jinja2>=2.4')
    requires.append('Mako')

setup(
    name='acrylamid',
    version=version,
    author='posativ',
    author_email='info@posativ.org',
    packages=find_packages(),
    include_package_data=True,
    url='http://posativ.org/acrylamid/',
    license='BSD revised',
    description='static blog compiler with incremental updates',
    data_files=[
        'README.rst',
    ],
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 3.2",
    ],
    install_requires=requires,
    tests_require=[
        'tox',
        'cram'
    ],
    entry_points={
        'console_scripts':
            ['acrylamid = acrylamid:Acryl']
    },
    **kw
)
