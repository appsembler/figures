=======
Figures
=======

|travis-badge| |codecov-badge|

Reporting and data retrieval app for `Open edX <https://open.edx.org/>`_.

.. _notice_section:

-----------------------------
Notice and Development Status
-----------------------------

**Figures is in development. We are targeting our first production ready version for October, 2018**

This Document
=============

* This document is a work in progress (WIP) as we work toward the initial production ready Figures release

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

--------------------
Project Architecture
--------------------

Front-end
=========

The Figures user interface is a JavaScript Single Page Application (SPA) built with React and uses the `create-react-app <https://github.com/facebook/create-react-app>`_ build scaffolding generator.

Back-end
========

The Figures back-end is a reusable Django app. It contains a set of REST API endpoints that serve a dual purpose of providing data to the front-end and to remote clients.

--------
Devstack
--------

This section covers installing and running Figures in Ginkgo devstack.

We use the label ``<project>`` as a placeholder for your local devstack project folder. This is the folder that contains the `Vagrantfile <https://github.com/edx/configuration/blob/open-release/ginkgo.master/vagrant/release/devstack/Vagrantfile>`_ for the project to which you are installing and running Figures. 


Installing Figures in Devstack
==============================

This section describes installing Figures in the Open edX "Ginkgo" release Devstack Vagrant environment. This is the ``open-release/ginkgo.master`` branch of edX's `edx-platform <https://github.com/edx/edx-platform/tree/open-release/ginkgo.master>`_ LMS.

To run the Figures front-end in Devstack, you will need to run a Webpack development server on port 3000 to serve the frontend assets. This is in addition to running the LMS. You do not need to run the CMS to run Figures in Devstack.


Figures uses `Django Webpack Loader <https://github.com/owais/django-webpack-loader>`_ to serve the React app from the LMS. You can learn more about how this works by reading the Django Webpack Loader README.

Prerequisites
-------------

These instructions expect that you have a running Ginkgo Vagrant based devstack and that you are working from a command line shell.


Steps
-----

1. Update the Vagrantfile 

You need to update the Vagrantfile to provide access to port 3000 from the VM to the host (your local system)

Edit your ``<project>/Vagrantfile``

Add the following line to the conditional block ``if not ENV['VAGRANT_NO_PORTS']``::

	config.vm.network :forwarded_port, guest: 3000, host: 3000  # Figures webpack server


After updating, this section should look like::

	  # If you want to run the box but don't need network ports, set VAGRANT_NO_PORTS=1.
	  # This is useful if you want to run more than one box at once.
	  if not ENV['VAGRANT_NO_PORTS']
	    config.vm.network :forwarded_port, guest: 8000, host: 8000  # LMS
	    config.vm.network :forwarded_port, guest: 8001, host: 8001  # Studio
	    config.vm.network :forwarded_port, guest: 8002, host: 8002  # Ecommerce
	    config.vm.network :forwarded_port, guest: 8003, host: 8003  # LMS for Bok Choy
	    config.vm.network :forwarded_port, guest: 8031, host: 8031  # Studio for Bok Choy
	    config.vm.network :forwarded_port, guest: 8120, host: 8120  # edX Notes Service
	    config.vm.network :forwarded_port, guest: 8765, host: 8765
	    config.vm.network :forwarded_port, guest: 9200, host: 9200  # Elasticsearch
	    config.vm.network :forwarded_port, guest: 18080, host: 18080  # Forums
	    config.vm.network :forwarded_port, guest: 8100, host: 8100  # Analytics Data API
	    config.vm.network :forwarded_port, guest: 8110, host: 8110  # Insights
	    config.vm.network :forwarded_port, guest: 9876, host: 9876  # ORA2 Karma tests
	    config.vm.network :forwarded_port, guest: 50070, host: 50070  # HDFS Admin UI
	    config.vm.network :forwarded_port, guest: 8088, host: 8088  # Hadoop Resource Manager
	    config.vm.network :forwarded_port, guest: 18381, host: 18381    # Course discovery
	    config.vm.network :forwarded_port, guest: 3000, host: 3000 # Figures webpack server
	  end

2. Clone the Figures repository

On your host, go to the ``<project>/src`` folder and run::

	git clone git@github.com:appsembler/figures.git

3. Install the Figures Python package

From your host's shell, ssh to the Vagrant VM::

	vagrant ssh

Change to the *edxapp* user::

	sudo su edxapp

Navigate to the Figures source directory::

	cd /edx/src/figures

Install the package with pip::

	pip install -e .

Figures should now be installed. To confirm, run the following::

	pip list | grep figures

You should see a line like::

	Figures (0.1.0, /edx/src/figures)


4. Update the Devstack LMS env file

Continuing as user *edxapp*, edit the ``/edx/app/edxapp/lms.env.json`` file.

As a top level key, add the following::

	"ADDL_INSTALLED_APPS": [
		"figures"
	]

We suggest adding the above immediately after ``ACTIVATION_EMAIL_SUPPORT_LINL`` so that it is in alphabetical order.

In the FEATURES section, add ``"ENABLE_FIGURES": true``::

	"FEATURES": {
		... 
		"ENABLE_FIGURES": true,
		...
	}


5. Update your edx-platform

You can update edx-platform from either the host or the VM. If you edit from the host, your edx-platform project is here::

	<project>/edx-platform

If you edit from within the VM, your edx-platform project is here::

	/edx/app/edxapp/edx-platform


Edit ``lms/urls.py`` to add the following to the bottom of the file::


	if settings.FEATURES.get('ENABLE_FIGURES'):
    	urlpatterns += (
    		url(r'^figures/',
    		    include('figures.urls', namespace='figures')),
    	)


Edit ``lms/envs/devstack.py`` to add the following to the bottom of the file::

	from figures.settings import FIGURES


6. Run migrations for Figures

In the Vagrant VM, as user *edxapp*, navigate to the following directory::

	/edx/app/edxapp/edx-platform

And run the following::

	./manage.py lms migrate figures


7. Install Figures front-end dependencies

As the *edxapp* user, navigate to the ``/edx/src/figures/frontend`` directory and run the following::

	npm install

This will install the `NPM <https://www.npmjs.com/>`_ dependencies.


You should now have your devstack ready to run.


Running Figures in Devstack
===========================

You will need two terminal windows open. One to start the LMS, the other to start the webpack development server for the Figures UI. In each, you should be user *edxapp*::

1. Start the webpack development server::

	cd /edx/src/figures/frontend
	npm start

This will start the Webpack development server on port 3000.


2. Start the LMS::

	cd /edx/app/edxapp/edx-platform

	paver devstack lms


3. Open the LMS in a browser on your host

	a. Go to ``localhost:8000`` and log in as a staff or admin user
	b. navigate to ``localhost:8000/figures/``


The Figures main page should now be displayed.


Production Installation
-----------------------

**NOTE: We're actively developing Figure toward production release this summer.** This means there are missing parts. Please see the notice_section_ section above. Also, these instructions are a work in progress (WIP). Your feedback is welcome so that we can improve the instructions**


This section describes installing Figures in Open edX "Ginkgo" release. This is the `open-release/ginkgo.master` branch of edX's `edx-platform <https://github.com/edx/edx-platform/tree/open-release/ginkgo.master>`_ LMS.

For installing on Appsembler's `edx-platform fork <https://github.com/appsembler/edx-platform/tree/appsembler/ginkgo/master>`_ read **<TODO: Insert link to instructions doc>**

Other custom installation options may be added in the future.


It is assumed you have an instance of Open edX Gingko running in either a devstack or production style environment.

Steps
~~~~~

*NOTE: Rework the instructions to do the edx-platform modifications first*

1. Shell to the running Ginkgo instance. Become the *edxapp* user

2. Install the ``figures`` Python package 

When we add Figures to `pypi <https://pypi.python.org/pypi>`_, then installers will be able to do ``pip install figures``

Until then::

	pip install -e git+https://github.com/appsembler/figures.git#egg=figures


3. Add the following to ``lms.env.json``::

	"ADDL_INSTALLED_APPS": [
		"figures"
	]

If you are enablinhg conditional operation of edx-figures in your edx-platform fork, then add ``ENABLE_FIGURES`` as a key-value pair under the ``FEATURES`` key as follows::

	"FEATURES": {
		... 
		"ENABLE_FIGURES": true,
		...
	}

*NOTE: You also have to enable conditional features by customizing your edx-platform fork.*


4. Update the LMS settings file(s)

To get Figures to work in Ginkgo, you will need to import ``figures.settings`` in one or more of the ``lms/envs/`` settings files. We suggest one of two approaches depending on whether you need to conditionally enable Figures.

If you do not need to conditionally enable Figures, then add the following to the bottom of ``lms/envs/common.py``::

	from figures.settings import FIGURES

If you do need to conditionally enable Figures, then we suggest adding a conditional import at the bottom of both the ``lms/envs/aws.py`` and ``lms/envs/devstack.py`` as follows::

	if FEATURES.get('ENABLE_FIGURES'):
		from figures.settings import FIGURES


The above are steps to follow if you don't have your own custom settings files. If you do use custom settings files, then we suggest adding the conditional import of figures.settings in those (custom settings file(s)) instead of ``aws.py`` and ``devstack.py``

A key point is to import the ``figures.settings`` module **after** ``WEBPACK_LOADER`` has been defined.


5. Update LMS `urls.py`::

	if settings.FEATURES.get('ENABLE_FIGURES'):
    	urlpatterns += (
    		url(r'^figures/',
    		    include('figures.urls', namespace='figures')),
    	)

6. Production: Restart the app server::

	sudo /edx/bin/supervisorctl restart edxapp:lms


At this time, the CMS settings do not need to be modified.





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


Future
------

Open edX "Hawthorn" will provide a plug-in architecture. This will hopefully simplify Figures installation.

How to Contribute
-----------------


TODO: Add details here or separate `CONTRIBUTING` file to the root of the repo

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@appsembler.com.


.. |travis-badge| image:: https://travis-ci.org/appsembler/figures.svg?branch=master
    :target: https://travis-ci.org/appsembler/figures/
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/figures/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/figures?branch=master
    :alt: Codecov

