from distutils.core import setup

setup(
    name='acrylamid',
    version='0.1.10',
    author='posativ',
    author_email='info@posativ.org',
    packages=['acrylamid'],
    scripts=['bin/acrylamid'],
    url='http://pypi.python.org/pypi/acrylamid/',
    license='LICENSE.txt',
    description='yet another static blog generator.',
    long_description=open('README.txt').read(),
    install_requires=[
        "jinja2 == 2.4.1",
        "Markdown >= 2.0.3",
    ],
)
