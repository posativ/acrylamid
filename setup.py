import sys; reload(sys)
sys.setdefaultencoding('utf-8')
import codecs
from distutils.core import setup

setup(
    name='acrylamid',
    version='0.1.10',
    author='posativ',
    author_email='info@posativ.org',
    packages=['acrylamid', 'acrylamid.filters', 'acrylamid.views'],
    scripts=['bin/acrylamid'],
    url='http://pypi.python.org/pypi/acrylamid/',
    license='LICENSE.txt',
    description='yet another static blog generator.',
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Internet",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ],
   install_requires=[
        'Jinja2>=2.4',
        'Markdown>=2.0.1'
    ],
)