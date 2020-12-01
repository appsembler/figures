=======
Figures
=======

|travis-badge| |codecov-badge|

Reporting and data retrieval app for `Open edX <https://open.edx.org/>`__.

.. _notice_section:


TBD Dec 2020 - Figures release 0.4.0 - prerelease
=================================================

_WIP release notes for 0.4.0_

* Juniper upgrade

  * https://github.com/appsembler/figures/pull/264

* MAU 2G data model and signal trigger

  * Needs to be added to Figures `master` branch

* Add database indexing

  * WIP

* Fix Figures URL wildcard placement

  * https://github.com/appsembler/figures/pull/284

* Documentation update

  * WIP

30 Oct 2020 - Figures release 0.3.19
====================================

* Fix the comparison showing N/A when comparing to zero

  * https://github.com/appsembler/figures/pull/277

* Fix Figures devsite settings

  * https://github.com/appsembler/figures/pull/278


26 Oct 2020 - Figures release 0.3.18
====================================

* FIX - Removed dependency on 'packaging.versions'

  * https://github.com/appsembler/figures/pull/272
  * NOTE: This PR updates a previous commit that required the `packaging` package


16 Oct 2020 - Figures release 0.3.17
====================================

* Reworked SiteMonthlyMetrics registered users metric. This was causing the `/figures/api/site-monthly-metrics/registered_users` endpoint to timeout with a 500 error

  * https://github.com/appsembler/figures/pull/268

* Fixed Ginkgo (Django Filter 0.11.0) Backward compatibility issues

  * https://github.com/appsembler/figures/pull/266
  * https://github.com/appsembler/figures/pull/269

* UI Bug fix: Add success feedback to csv export dialog

  * https://github.com/appsembler/figures/pull/265

* Bump http-proxy from 1.18.0 to 1.18.1 in /frontend

  * https://github.com/appsembler/figures/pull/254


28 Sep 2020 - Figures release 0.3.16
====================================

* Add Learners Progress Overview to main menu

  * https://github.com/appsembler/figures/pull/256

* Performance and test improvement for LearnerMetricsViewSet

  * https://github.com/appsembler/figures/pull/260

* Fix code that doesn't work on Ginkgo (Django 1.8)

  * https://github.com/appsembler/figures/pull/261


11 Sep 2020 - Figures release 0.3.15
====================================

* Learner progress overview UI improvements

  * https://github.com/appsembler/figures/pull/255


24 Aug 2020 - Figures release 0.3.14
====================================

* Added multi-course filtering to the `learner-metrics` API endpoint

  * https://github.com/appsembler/figures/pull/248

* Small cosmetic issues in new Learners Progress Overview page

  * https://github.com/appsembler/figures/pull/247


14 Aug 2020 - Figures release 0.3.13
====================================

* Learner metrics Prerelease API and UI

  * https://github.com/appsembler/figures/pull/239
  * https://github.com/appsembler/figures/pull/240

* Improve logging for monthly metrics pipeline and set default to run the monthly metrics pipeline task

  * https://github.com/appsembler/figures/pull/242

* Bug fix: Site level certificate metrics

  * https://github.com/appsembler/figures/pull/244


15 Jul 2020 - Figures release 0.3.12
====================================

* Adds enrollment metrics API endpoint

  * https://github.com/appsembler/figures/pull/233

* Site monthly metrics API performance improvement

  * https://github.com/appsembler/figures/pull/234

* Initial implementation of Celery support for Figures devsite

  * https://github.com/appsembler/figures/pull/215


29 Jun 2020 - Figures release 0.3.11
====================================

* Fixes incorrect site monthly metrics course completion data

  * https://github.com/appsembler/figures/pull/219

* Fixes CourseDailyMetricsSerializer when average_progress is 1.00

  * https://github.com/appsembler/figures/pull/230

* Updates pipeline enrollment metrics queries to improve performance

  * https://github.com/appsembler/figures/pull/226

* Added site pipeline progress indicator to logging

  * https://github.com/appsembler/figures/pull/228

* Bump devsite Django 1.11 to version 1.11.29

  * https://github.com/appsembler/figures/pull/227

* Bump websocket-extensions from 0.1.3 to 0.1.4 in /frontend

  * https://github.com/appsembler/figures/pull/222


21 May 2020 - Figures release 0.3.10
====================================

* Improved daily metrics pipeline performance

  * https://github.com/appsembler/figures/pull/214

* Bug fixes

  * https://github.com/appsembler/figures/pull/213


24 Apr 2020 - Figures release 0.3.9
===================================

* Updated UI, MAU fix, style fixes, label changes
* Added site monthly metrics scheduled tasks to fill last month's MAU
* Added Django Debug Toolbar to devsite


10 Apr 2020 - Figures release 0.3.8
===================================

* Performance improvement to "Site Monthly Metrics" active users endpoint


8 Apr 2020 - Figures release 0.3.7
==================================

* Updated UI to improve performance and usability
* Added "Course Monthly Metrics" set of API endpoints


16 Feb 2020 - Figures release 0.3.6
===================================

* Updated UI to address performance issues
* Added missing `organizations` to devsite settings `INSTALLED_APPS`


20 Feb 2020 - Figures release 0.3.5
====================================

Client (UI and API) facing updates

* Site Monthly Metrics pipeline and new API endpoints
* Added Course MAU metrics API endpoint and pipeline
* Added user email address to general user data
* Bug fix - URL pattern fix for `figures/`

Developer facing updates

* Updated Django micro version to Figures devsite
* Added missing `.env` file for Makefile support
* Added Pylint to testing
* Refactored permissions module


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
