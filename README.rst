edX Figures 
===========

Reporting and data retrieval app for Open edX


Overview
--------



Requirements
------------

* Python (2.7)
* Django (1.8)
* Open edX (Ficus)


Installation
------------

This section describes two ways of adding edx-figures to Open edX Ficus, depending on if you are running edx.org's version or Appsembler's fork of
``edx-platform``


Common steps
~~~~~~~~~~~~

For both, do the following:

1. Install edx-figures. ``pip install edx-figures``

2. Add the following to ``lms.env.json``::

	"ADDL_INSTALLED_APPS": [
		"edx_figures"
	]


Appsembler's Fork of edx-platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are running Appsembler's fork, add the following to ``lms.env.json``::

    "APPSEMBLER_FEATURES": {
        "ENABLE_EDX_FIGURES": true,
        "LMS_URLS_INCLUDE": [
            "^figures", "edx_figures.urls"
        ],
	}

If there are existing entries in ``ADDL_INSTALLED_APPS``, just add ``edx_figures`` to the list. If ``ADDL_INSTALLED_APPS`` does **not** exist, then add it to the ``lms.env.json`` file.


edx.org version of edx-platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are running edx.org's version, you will need to customize your LMS settings ``aws.py`` file.

Add the following to the ``lms/envs/aws.py`` file

::

	from edx_figures.settings import EDX_FIGURES

If you want to override any of the values in edx_figures.settings, you can create a key in lms.env.json (for example, ``EDX_FIGURES_SETTINGS``) and update the settings

so your aws.py file would have this addition::

	from edx_figures.settings import EDX_FIGURES

	EDX_FIGURES.update(ENV_TOKENS.get('EDX_FIGURES', {}))


This will override any **top level** key/value pairs in the ``edx-figures.settings.EDX_FIGURES`` dict


Front-end Client App
--------------------

edx-figures has a skelton React app and simple/minimal webpack build configuration.
This initial version only compiles assets, does not do live loading in development mode. We'll add that as we build out the front end.

Configure your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Install version 0.5.0 of ``django-webpack-loader``. First shell into the server, then run::

	sudo su edxapp -s /bin/bash
	cd
	source edxapp_env
	pip install django-webpack-loader==0.5.0

Install ``edx-figures``. There are different ways to install this. For development, we likely want to clone the repo into a local branch and ``pip innstall -e`` 

For production with the Appsembler provisioning infrastructure, we can add ``edx-figures`` to the deployment's ``private_requirements.txt`` file. 


Update your lms.env.json file. Add ``webpack_loader`` to the existing ``edx_figures`` in ``ADDL_INSTALLED_APPS`` setting::

    "ADDL_INSTALLED_APPS": [
    	"edx_figures",
    	"webpack_loader"
    ]


Also to ``lms.env.json``, add ``EDX_FIGURES`` setting as a top level setting and set its property ``ENABLED`` to `true`. We will be adding more settings as we develop edx-figures. For now::

    "EDX_FIGURES": {
        "ENABLED": true
    }



Install packages
~~~~~~~~~~~~~~~~

Open a shell, or reuse the one for which you installed ``django-webpack-loader``. Become the edxapp user and navigate to the ``edx-figures`` directory. If you are on devstack, it should be ``/edx/src/edx-figures/``. Then run::

	npm install

This should install your required packages in the ``edx-figures`` ``packages.json`` file.

To build a new bundle::

	webpack

If you are in production/staging, then you may need to rebuild your assets. If you are on devstack, you won't need to.


Compiling your JavaScript assets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
to compile the React app:



Then navigate to the `/figures/` endpoint on the sever. For devstack, this would be `http://localhost:8000/figures/`

You should see a "Welcome to edX Figures" header


Future
------

Ginkgo support is underway


Documentation
-------------

TODO: Add documentation

How to Contribute
-----------------

TODO: Fill in details