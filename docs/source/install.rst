.. _install:


**NOTICE:** These instructions are for Ficus and Ginkgo and need to be updated for Hawthorn


==================
Installing Figures
==================

This document describes how to install and configure Figures to run in Open edX.


Please note that we're currently focused on developing and troubleshooting Figures, and *not* general Open edX/devstack issues.

If you encounter any issues with installing or running Figures, please first ensure that your installation is working correctly and that the problem is with Figures. 

Please see the documentation `Installing, Configuring, and Running the Open edX Platform <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/>`__ for guidance in getting Open edX set up.

If you run into issues installing Open edX and cannot find an answer in the above Open edX installation instructions, you can post your issue in Open edX slack #general or #ops channels.

Once you know that you've got your base Open edX environment working and you are certain the issue with with Figures, please file an issue in `Figures github issues <https://github.com/appsembler/figures/issues>`__.


------------
Requirements
------------

For all Open edX releases:

* Python (2.7)

For Hawthorn:

* Django (1.11)

For Ficus and Ginkgo:

* Django (1.8)

--------
Devstack
--------

Please see the :ref:`devstack <devstack>` documentation for instructions on how to install and configure Figures for devstack.

-------------------------
Production (cloud server)
-------------------------

This section describes how to install Figures on Open edX "Ginkgo". This is the `open-release/ginkgo.master` branch of edX's `edx-platform <https://github.com/edx/edx-platform/tree/open-release/ginkgo.master>`_ LMS.

This can be a production server, staging, or close based development server. For purposes of the instructions here, we will assume the target is a production environment.

Overview
========

We're going to describe *what* needs to happen to get Figures installed, along with instructions on how to perform each step manually. 

These steps are required to install and configures Figures:

* Add Figures to the edxapp Python packages
* Add Figures to the installed apps in the LMS settings
* Add Figures to the LMS settings
* Add Figures to the LMS URL patterns
* Run migrations to include Figures models
* Restart the LMS 

**You will need shell access and ability to sudo as the edxapp user for the Open edX instance on which you are installing Figures.**

*At this time, the CMS settings do not need to be modified.*

The following goes into detail for each step.

Steps
=====


Add Figures to the edxapp Python packages
-----------------------------------------

Figures needs to be added to the edxapp Python virtualenv packages.

Step 1
~~~~~~

Shell to the server hosting Open edX

Step 2 
~~~~~~

Run ``sudo su edxapp -s /bin/bash`` to switch to the edxapp user

Step 3 
~~~~~~

Verify you are using the ``edxapp`` user's virtualenv. Run ``which pip`` to check if the Python virtualenv is enabled. you should see:

::

	/edx/app/edxapp/venvs/edxapp/bin/pip

If you don't, then run ``source ~./edxapp_env`` and check again to verify

Step 4 
~~~~~~

Run ``pip install figures`` to install Figures from PyPI.

Alternate Steps
^^^^^^^^^^^^^^^

Alternately you can install Figures from source by doing the following:

Step 1
~~~~~~

Follow steps 1-3 above first

Step 2
~~~~~~

Install from Github in edit mode:

::

	pip install -e git+https://github.com/appsembler/figures.git#egg=figures

You may want to do this if you want to run from master. This is not recommended for production environments.


Add Figures to the installed apps in the LMS settings
-----------------------------------------------------

Figures needs to be in the ``INSTALLED_APPS`` list in the LMS settings. For those familiar with Django, this is no different than any Django reusable app.

There are differnt ways to do this. Two ways are:

* Add Figures to the ``lms.env.json`` file
* Add to the LMS settings files (in the ``lms/envs/`` directory)

Open edX lets you add Django reusable apps via the ``lms.env.json`` file. This is the preferred approach as it reduces customization of ``edx-platform``

Add the following as a top level key to ``/edx/app/edxapp/lms.env.json``:

::

    "ADDL_INSTALLED_APPS": [
        "figures"
    ],

If ``ADDL_INSTALLED_APPS`` already exists, then just add ``"figures"`` to the list.

The other option is to add ``figuress`` directly to the ``INSTALLED_APPS`` list in the LMS settings file, ``lms/envs/common.py``


Add Figures to the LMS settings
-------------------------------

Figures needs to be found by Django Webpack Loader in order to serve its UI. It also needs to be registered with the Celerybeat scheduler in order to run the ETL pipeline on a schedule.

Figures can do this automatically if its settings are loaded when the LMS starts up by having ``figures.settings`` be imported in the LMS settings.

At the bottom of the ``lms/envs/aws.py`` file, add the following:

::

	if 'figures' in INSTALLED_APPS:
	    import figures
	    figures.update_settings(
	        WEBPACK_LOADER,
	        CELERYBEAT_SCHEDULE,
	        ENV_TOKENS.get('FIGURES', {}))

**IMPORTANT**: Make sure that you do the above import *AFTER* ``WEBPACK_LOADER`` and ``CELERYBEAT_SCHEDULE`` have been declared in the LMS envs.

If you have implemented your own wrapper around ``lms/envs/aws.py`` you can add the above to that file instead. For example, Appsembler has ``aws_appsembler.py`` and ``devstack_appsembler.py`` for cloud deployments and devstack environments respectively.


Add Figures to the LMS URLconf
------------------------------

To access the Figures UI, the LMS needs to have its `URLconf <https://docs.djangoproject.com/en/1.8/topics/http/urls/>`_ updated to include Figures.

At the bottom of the ``lms/urls.py`` file, add the following:

::

	if 'figures' in settings.INSTALLED_APPS:
		urlpatterns += (
			url(r'^figures/',
			    include('figures.urls', namespace='figures')),
		)	


Run migrations to include Figures models
----------------------------------------

Figures contains its own models which are used for storing metrics data. Because of this, you need to create database tables for Figures models.

As the ``edxapp`` user, run the following:

::

	./manage.py lms migrate figures


Restart the LMS 
---------------

Since Figures needs to add entries to the ``WEBPACK_LOADER`` and ``CELERYBEAT_SCHEDULE`` settings vars, you need to restart the LMS Django app server.

*NOTE:* You do **NOT** have to restart Nginx or the host.

Exit the ``edxapp`` user to go back to the admin shell.

Run the following:

::

	sudo /edx/bin/supervisorctl restart edxapp:lms

Although it shouldn't be necessary, you can restart both the LMS and CMS by running:

::

	sudo /edx/bin/supervisorctl restart edxapp:


------------------------------------
Installing Figures in Open edX Forks
------------------------------------

Please see the :ref:`Appsembler <appsembler_install>` installation instructions for instructions specific to Appsembler's fork of edx-platform.

* TODO: Add instructions for community members to add instructions for their own ``edx-platform`` forks
