'''

If we want to exclude the top level 'tests' from the build, change the line:

::

    packages=find_packages(),

to

::

    packages=find_packages(exclude=['tests.*', 'tests']),

'''

from __future__ import absolute_import
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'docs/readme-pypi.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='Figures',
    version='0.4.dev12',
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
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points={
        'lms.djangoapp': [
            'figures = figures.apps:FiguresConfig',
        ],
    },
    install_requires=[
        'sqlparse >= 0.2.2',  # This is the requirement specified by Django 2.2+
    ],
)
