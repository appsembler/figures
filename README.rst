=======
Figures
=======

|travis-badge| |codecov-badge|

Reporting and data retrieval app for `Open edX <https://open.edx.org/>`_.

.. _notice_section:

-----------------------------
Notice and Development Status
-----------------------------


October 7, 2018
===============

**We're almost there!**

We're wrapping up the final steps to roll out Figures initial release this week:

* Update the installation and configuration instructions (meaning the instructions below will change)
* Update the front end (JavaScript React app) package dependencies to addres known security issues
* Build and add the static assets to the Figures Django reusable app
* Push and test to PyPI testing, validate the package
* Push to production PyPI


--------
Overview
--------

Figures is a reporting and data retrieval app. It plugs into the edx-platform LMS app server. Its goal is to provide site-wide and cross-course analytics that compliment Open edX's traditional course-centric analytics.

To evolve Figures to meet community needs, we are keeping in mind as principles the following features, which Jill Vogel outlined in her `lightweight analytics <https://edxchange.opencraft.com/t/analytics-lighter-faster-cheaper/202>`_ post on ed Xchange:

* Real time (or near real time) updates
* Lightweight deployment
* Flexible reporting
* Simpler contributions

Please refer to the Figures `design document <https://docs.google.com/document/d/16orj6Ag1R158-J-zSBfiY31RKQ5FuSu1O5F-zpSKOg4/>`_ for more details on goals and architecture.


------------
Requirements
------------

* Python (2.7)
* Django (1.8)
* Open edX (Ginkgo)

------------
Installation
------------

Devstack
========

Go `here <docs/source/devstack.rst>`_ for instructions to install and run Figures in devstack.

Production
==========

go `here <docs/source/install.rst>`_ for instructions to install Figures in production.

--------------------
Project Architecture
--------------------

Front-end
=========

The Figures user interface is a JavaScript Single Page Application (SPA) built with React and uses the `create-react-app <https://github.com/facebook/create-react-app>`_ build scaffolding generator.

Back-end
========

The Figures back-end is a reusable Django app. It contains a set of REST API endpoints that serve a dual purpose of providing data to the front-end and to remote clients.


-------
Testing
-------

*TODO: Improve the testing instructions*

The unit tests **should** be able to run on any OS that supports Python 2.7.x

Clone the repo:
::
 	git@github.com:appsembler/figures.git

Go to the project directory:
::
	cd figures

Create a `virtualenv <https://virtualenv.pypa.io/en/stable/>`_.

Install required Python packages:
::
	pip install -r devsite/requirements.txt

From the `figures` repository root directory:
::
	pytest

If all goes well, the Figures unit tests will all complete succesfully

------
Future
------

Open edX "Hawthorn" will provide a plug-in architecture. This will hopefully simplify Figures installation.

-----------------
How to Contribute
-----------------


TODO: Add details here or separate `CONTRIBUTING` file to the root of the repo

-------------------------
Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@appsembler.com.


.. |travis-badge| image:: https://travis-ci.org/appsembler/figures.svg?branch=master
    :target: https://travis-ci.org/appsembler/figures/
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/figures/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/figures?branch=master
    :alt: Codecov

