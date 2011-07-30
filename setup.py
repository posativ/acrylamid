from distutils.core import setup

setup(
    name='lilith',
    version='0.1.7',
    author='posativ',
    author_email='info@posativ.org',
    packages=['lilith'],
    scripts=['bin/lilith'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/lilith/',
    license='LICENSE.txt',
    description='yet another static blog generator.',
    long_description=open('README.txt').read(),
)
