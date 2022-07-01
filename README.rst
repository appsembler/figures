=======
Figures
=======

|travis-badge| |codecov-badge|

Reporting and data retrieval app for `Open edX <https://open.edx.org/>`__.

.. _notice_section:

`Figures is on PyPI <https://pypi.org/project/Figures/>`__


Mar 3, 2022 - Figures release 0.4.2
===================================

This release adds an optionan new pipeline workflow

For details, `please read here <https://github.com/appsembler/figures/issues/428>`__

To enable this feature, you need to update the LMS settings (aka 'server-vars.yml') as follows:

server-vars.yml::

  FIGURES: 
    DAILY_TASK: 'figures.tasks.populate_daily_metrics_next'

In Django settigs, you would check the var here::

  from django.conf import settings
  settings.ENV_TOKENS['FIGURES'].get('DAILY_TASK')

PR about the workflow update:

* Pipeline improvement prerequisites 

  * https://github.com/appsembler/figures/pull/427

* Figures pipeline performance improvement 

  * https://github.com/appsembler/figures/pull/429

* Fix enrollment data backfill Django management command

  * https://github.com/appsembler/figures/pull/432

Other PRs

* Revert devsite 'courseware' app namepace back to originial

  * https://github.com/appsembler/figures/pull/434

* Bump url-parse from 1.5.1 to 1.5.10 in /frontend

  * https://github.com/appsembler/figures/pull/431

* Bump urijs from 1.19.6 to 1.19.8 in /frontend

  * https://github.com/appsembler/figures/pull/430


Feb 4, 2022 - Main Branch
=========================

`main` is the new default branch


Jan 28, 2022 - Figures release 0.4.1
====================================

Figures 0.4.1 is finally here. After several development releases, we realized it was time to just move to production releases.




Figures 0.4.x release series supports Open edX Juniper, Hawthorn, and Ginkgo


Please visit Figures `releases page <https://github.com/appsembler/figures/releases>`__ for details on specific releases.


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


-------------
Configuration
-------------

Figures can be configured via Django settings' ``FIGURES`` key. Open edX reads configuration from
the ``/edx/etc/lms.yml`` file both in devstack and production servers. In releases before Juniper it
was the ``lms.env.json`` file.

A Figures configuration may look like the following:


::

	FEATURES:  # The standard Open edX feature flags
		# ... other features goes here ...
		FIGURES_IS_MULTISITE: True
		# ... more features goes there ...

	FIGURES:  # Other Figures configurations
		SITES_BACKEND: 'openedx.core.djangoapps.appsembler.sites.utils:get_active_sites'
		REQUESTED_SITE_BACKEND: 'tahoe_figures_plugins.sites:get_current_site_or_by_uuid'
		FIGURES_PIPELINE_TASKS_ROUTING_KEY: 'edx.lms.core.high'
		DAILY_METRICS_IMPORT_HOUR: 13
		DAILY_METRICS_IMPORT_MINUTE: 0


Settings like ``SITES_BACKEND`` require a path to a Python function or class. The path is consists of two parts:
a Python module e.g. ``my_plugin_package.helpers`` and an object e.g ``my_helper`` separated by a colon e.g.
``my_plugin_package.helpers:my_helper``.

This object would be imported by the ``import_from_path`` helper in the
`figures/helpers.py <https://github.com/appsembler/figures/blob/932eeab84c469a34dfcb94232bbe6f7c08146b3f/figures/helpers.py#L84-L98>`__ module.

.....................
Configuration options
.....................


* ``FEATURES.FIGURES_IS_MULTISITE`` (default ``False``): Boolean feature flag to run Figures in a single-site mode by
  default (when set to ``False``) most popular Open edX installation option.
  The multisite mode requires a custom ``edx-organizations`` fork that is used for
  Appsembler Tahoe clusters.

* ``FIGURES.SITES_BACKEND`` (default ``None``): A Python path to function to list figures sites.
  For example, this is useful to customize which sites are processed and which are considered inactive.
  By default (when ``None`` is used) all sites are listed in the multi-site mode.

* ``REQUESTED_SITE_BACKEND`` (default ``None``): Python path to a function that gets the current site.
  For example it can be used for API purposes to pass a Site ID to get a different site.
  By default (when ``None`` is used) the Django's ``get_current_site()`` helper is used.


**TBD:** Document ``FIGURES_PIPELINE_TASKS_ROUTING_KEY``, ``DAILY_METRICS_IMPORT_HOUR`` and ``DAILY_METRICS_IMPORT_MINUTE``.

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
