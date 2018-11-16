'''

If we want to exclude the top level 'tests' from the build, change the line:

::

    packages=find_packages(),

to

::

    packages=find_packages(exclude=['tests.*', 'tests']),

'''

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'docs/readme-pypi.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='Figures',
    version='0.1.5',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Reporting and data retrieval for Open edX',
    long_description=README,
    url='https://github.com/appsembler/figures',
    author='Appsembler',
    author_email='opensources@appsembler.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
