.. _devstack:


**NOTICE:** These instructions are for Ficus and Ginkgo devstacks running Vagrant and need to be updated for Hawthorn docker devstack


===================
Figures on Devstack
===================

This document covers installing and running Figures in **Ginkgo** devstack.

We use the label ``<project>`` as a placeholder for your local devstack project folder. This is the folder that contains the `Vagrantfile <https://github.com/edx/configuration/blob/open-release/ginkgo.master/vagrant/release/devstack/Vagrantfile>`_ for the project to which you are installing and running Figures. 

------------------------------
Installing Figures in Devstack
------------------------------

This section describes installing Figures in the Open edX "Ginkgo" release Devstack Vagrant environment. This is the ``open-release/ginkgo.master`` branch of edX's `edx-platform <https://github.com/edx/edx-platform/tree/open-release/ginkgo.master>`_ LMS.

To run the Figures front-end in Devstack, you will need to run a Webpack development server on port 3000 to serve the frontend assets. This is in addition to running the LMS. You do not need to run the CMS to run Figures in Devstack.

Figures uses `Django Webpack Loader <https://github.com/owais/django-webpack-loader>`_ to serve the React app from the LMS. You can learn more about how this works by reading the Django Webpack Loader README.


**NOTE** The following instructions assume that you are setting up devstack for active figures development.


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

	Figures (0.1.3, /edx/src/figures)


4. Update the Devstack LMS env file

Continuing as user *edxapp*, edit the ``/edx/app/edxapp/lms.env.json`` file.

As a top level key, add the following::

	"ADDL_INSTALLED_APPS": [
		"figures"
	]

We suggest adding the above immediately after ``ACTIVATION_EMAIL_SUPPORT_LINK`` so that it is in alphabetical order.


5. Update your edx-platform

You can update edx-platform from either the host or the VM. If you edit from the host, your edx-platform project is here::

	<project>/edx-platform

If you edit from within the VM, your edx-platform project is here::

	/edx/app/edxapp/edx-platform


Edit ``lms/urls.py`` to add the following to the bottom of the file::

	if 'figures' in settings.INSTALLED_APPS:
		urlpatterns += (
			url(r'^figures/',
			    include('figures.urls', namespace='figures')),
		)	


Edit ``lms/envs/devstack.py`` to add the following to the bottom of the file::

	if 'figures' in INSTALLED_APPS:
	    import figures
	    figures.update_settings(
	        WEBPACK_LOADER,
	        CELERYBEAT_SCHEDULE,
	        ENV_TOKENS.get('FIGURES', {}))


6. Run migrations for Figures

In the Vagrant VM, as user *edxapp*, navigate to the following directory::

	/edx/app/edxapp/edx-platform

And run the following::

	./manage.py lms migrate figures --settings=<environment settings>

Where ``environment settings`` is ``devstack`` for the default named release. Individual organizations may tailor their environment settings. Appsembler uses ``devstack_appsembler`` for its fork::

	./manage.py lms migrate figures --settings=devstack_appsembler


7. Install Figures front-end dependencies

As the *edxapp* user, navigate to the ``/edx/src/figures/frontend`` directory and run the following::

	npm install

This will install the `NPM <https://www.npmjs.com/>`_ dependencies.


You should now have your devstack ready to run.


Running Figures in Devstack
===========================

You will need two terminal windows open. One to start the LMS, the other to start the webpack development server for the Figures UI. In each, you should be user *edxapp*:

Step 1. Start the webpack development server::

	cd /edx/src/figures/frontend
	npm start

This will start the Webpack development server on port 3000.


Step 2. Start the LMS::

	cd /edx/app/edxapp/edx-platform

	paver devstack lms


Step 3. Open the LMS in a browser on your host

	a. Go to ``localhost:8000`` and log in as a staff or admin user
	b. navigate to ``localhost:8000/figures/``


The Figures main page should now be displayed.
