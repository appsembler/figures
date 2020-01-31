=======
Figures
=======

|travis-badge| |codecov-badge|

Reporting and data retrieval app for `Open edX <https://open.edx.org/>`__.

.. _notice_section:


29 Jan 2020 - Figures release 0.3.4
====================================

* Hawthorn support since release 0.3.0
* This release includes bug fixes, UI improvements, and backport support for Ginkgo
* Includes a standalone development mode. See the `developer quickstart guide <./DEVELOPER-QUICKSTART.md/>`__


--------
Overview
--------

Figures is a reporting and data retrieval app. It plugs into the edx-platform LMS app server. Its goal is to provide site-wide and cross-course analytics that compliment Open edX's traditional course-centric analytics.

To evolve Figures to meet community needs, we are keeping in mind as principles the following features, which Jill Vogel outlined in her `lightweight analytics <https://edxchange.opencraft.com/t/analytics-lighter-faster-cheaper/202>`__ post on ed Xchange:

* Real time (or near real time) updates
* Lightweight deployment
* Flexible reporting
* Simpler contributions

Please refer to the Figures `design document <https://docs.google.com/document/d/16orj6Ag1R158-J-zSBfiY31RKQ5FuSu1O5F-zpSKOg4/>`__ for more details on goals and architecture.

------------
Requirements
------------

For all Open edX releases:

* Python (2.7)

For Hawthorn:

* Django (1.11)

For Ginkgo:

* Django (1.8)



.. _installation:

------------
Installation
------------

*NOTICE: Installation instructions are out of date and backlogged for update*


Devstack
========

Go `here <docs/source/devstack.rst>`__ for instructions to install and run Figures in devstack.

Production
==========

Go `here <docs/source/install.rst>`__ for instructions to install Figures in production.

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

Create a `virtualenv <https://virtualenv.pypa.io/en/stable/>`__ for Python 2.7.x.

Install required Python packages:

::

	pip install -r devsite/requirements.txt

From the `figures` repository root directory:

::

	py.test

If all goes well, the Figures unit tests will all complete succesfully

------
Future
------

* Open edX "Hawthorn" will provide a plug-in architecture. This will hopefully simplify Figures installation even more
* Downloadable report files
* Plugin architecture to extend Figures for custom data sources


-----------------
How to Contribute
-----------------


TODO: Add details here or separate `CONTRIBUTING` file to the root of the repo


.. _reporting_issues:

----------------
Reporting Issues
----------------

If you find bugs or run into issues, please submit an issue ticket to the `Figures issue tracker <https://github.com/appsembler/figures/issues>`__ on Github.

.. _reporting_security_issues:

Reporting Security Issues
=========================

Please do not report security issues in public. Please email security@appsembler.com.


.. |travis-badge| image:: https://travis-ci.org/appsembler/figures.svg?branch=master
    :target: https://travis-ci.org/appsembler/figures/
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/figures/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/figures?branch=master
    :alt: Codecov
