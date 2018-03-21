edX Figures 
===========

Reporting and data retrieval app for Open edX

Notice
------

**This document is a work in progress (WIP) as we develop the initial edx-figures release.**

Overview
--------

edX Figures is a reporting and data retrieval app. It plugs into the edx-platform LMS app server. Its goal is to fill the gaps in Open edX to meet the reporting needs of the community.

To evolve edx-figures to meet community needs, we are keeping in mind as principles the following features, which Jill Vogel outlined in her post on ed Xchange:

* Real time (or near real time) updates
* Lightweight deployment
* Flexible reporting
* Simpler contributions

Please refer to the edX Figures `design document <https://docs.google.com/document/d/16orj6Ag1R158-J-zSBfiY31RKQ5FuSu1O5F-zpSKOg4/>` for more details on goals and architecture.

Requirements
------------

* Python (2.7)
* Django (1.8)
* Open edX (Ginkgo)


Installation
------------

**NOTE: These instructions are a WIP and incomplete**

This section describes installing edx-figures in Open edX "Ginkgo" release. This is the `open-release/ginkgo.master` branch of edX's `edx-platform <https://github.com/edx/edx-platform/tree/open-release/ginkgo.master>` LMS.

For installing on Appsembler's `edx-platform fork <https://github.com/appsembler/edx-platform/tree/appsembler/ginkgo/master>` read `TODO: Insert link to instructions doc`

Other custom installation options may be added in the future.

It is assumed you have an instance of Open edX Gingko running in either a devstack or production style environment.

Steps
~~~~~

*NOTE: Rework the instructions to do the edx-platform modifications first*

1. Shell to the running Ginkgo instance. Become the edxapp user

2. Install the edx-figures Python package 

When we add edx-figures to `pypi <https://pypi.python.org/pypi>`, then installers will be able to do ``pip install edx-figures``

Until then::

	pip install -e git+https://github.com/appsembler/edx-figures.git#egg=edx-figures


3. Add the following to ``lms.env.json``::

	"ADDL_INSTALLED_APPS": [
		"edx_figures"
	]

If you are enablinhg conditional operation of edx-figures in your edx-platform fork, then add ``ENABLE_EDX_FIGURES`` as a key-value pair under the ``FEATURES`` key as follows::

	"FEATURES": {
		... 
		"ENABLE_EDX_FIGURES": true,
		...
	}

*NOTE: You also have to enable conditional features by customizing your edx-platform fork.*


4. Update the LMS settings file(s)

To get edx-figures to work in Ginkgo, you will need to import ``edx_figures.settings`` in one or more of the ``lms/envs/`` settings files. We suggest one of two approaches depending on whether you need to conditionally enable edx-figures.

If you do not need to conditionally enable edx-figures, then add the following to the bottom of ``lms/envs/common.py``::

	from edx_figures.settings import EDX_FIGURES

If you do need to conditionally enable edx-figures, then we suggest adding a conditional import at the bottom of both the ``lms/envs/aws.py`` and ``lms/envs/devstack.py`` as follows:

	if FEATURES.get('ENABLE_EDX_FIGURES'):
		from edx_figures.settings import EDX_FIGURES	


The above are steps to follow if you don't have your own custom settings files. If you do use custom settings files, then we suggest adding the conditional import of edx_figures.settings in those (custom settings file(s)) instead of ``aws.py`` and ``devstack.py``

A key point is to import the ``edx_figures.settings`` module **after** ``WEBPACK_LOADER`` has been defined.


5. Update LMS `urls.py`

::
	if settings.FEATURES.get('ENABLE_EDX_FIGURES'):
    	urlpatterns += (
    		url(r'^figures/',
    		    include('edx_figures.urls', namespace='edx-figures')),
    	)

6. Production: Restart the app server

::
	sudo /edx/bin/supervisorctl restart edxapp:lms


At this time, the CMS settings do not need to be modified.


Project Architecture
--------------------

Front-end
~~~~~~~~~

The edx-figures user interface is a JavaScript Single Page Application (SPA) built with React and uses the `create-react-app <https://github.com/facebook/create-react-app>` build scaffolding generator.

Back-end
~~~~~~~~~

The edx-figures back-end is a reusable Django app. It contains a set of REST API endpoints that serve a dual purpose of providing data to the front-end and to remote clients.


Testing
-------

TODO: Fill in this section

Future
------

Open edX "Hawthorn" will provide a plug-in architecture. 

Contributing
------------

TODO: Add details here or separate `CONTRIBUTING` file to the root of the repo



