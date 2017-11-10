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


Future
------

Ginkgo support is underway


Documentation
-------------

TODO: Add documentation

How to Contribute
-----------------

TODO: Fill in details