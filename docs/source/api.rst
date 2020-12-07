.. _figures_api:

###########
Figures API
###########

************
Architecture
************

Figures has a Django REST Framework (DRF) based REST API. 

The architecture used is mostly ``ViewSet`` based. For URL dispatching, the DRF ``DefaultRouter`` is used in ``figures.urls``


The Django REST Framework version used is dictated by the instance of Open edX in which Figures runs:

* For Ginkgo: ``djangorestframework==3.2.3``
* For Hawthorn: ``djangorestframework==3.6.3``
* For Juniper: ``djangorestframework==3.9.4``

Up to and including 0.4, the primary consumer of Figures API has been the frontend UI. Therefore versioning of the API has not been required. We plan to implement API versioning for Figures 0.5.

*****************
API Documentation
*****************

For Figures 0.4, we are beginning our effort to prepare the APIs for remote client use. With this is our intial effort to provide API documentation by generating OpenAPI 2.0 specification docs.


To enable API documenation generation on Figures devsite, you will need to run Figures in Juniper mode using Python 3.8, install the required Python package(s) and enable the OpenAPI settings flag.

1. Create or instantiate a Python 3.8 virtual env
2. Run ``pip install -r devsite/requirements/development_juniper.txt``
3. Set the following in ``figures/devsite/.env`` file::

	OPENEDX_RELEASE=JUNIPER
	ENABLE_OPENAPI_DOCS=true


Now you can start devsite.

1. Go to the ``devsite`` directory and run ``./manage.py migrate``
2. Run ``./manage.py createsuperuser`` to create an account, as the API requires authorized access
3. Start the web server: ``./manage.py runserver``
4. Open a browser and navigate to the main page, ``http://localhost:8000``
5. Login with the credentials you created in step 2
6. Navigate to one of the following URLs::

	http://localhost:8000/api-docs/

	http://localhost:8000/api-docs.json

	http://localhost:8000/redoc/

Now we have basic API documentation generation, the next phase is to update Figures views docstrings to make the documenation more usable.

============
OpenAPI Docs
============

Figures 0.4 uses `DRF - Yet another Swagger generator 2 <https://github.com/JoelLefkowitz/drf-yasg>`_, version ``1.19.4``  for the intial documentation approach.

---------------
Some Background
---------------

``drf-yasg2`` is a fork from ``drf-yasg``. According to the ``drf-yasg2`` Github repo README, It was forked because ``drf-yasg`` was not being maintained. The last ``drf-yasg`` version was 1.17.1. Work resumed and ``drf-yasg`` has a new ``1.20.0`` version. See the `release history <https://pypi.org/project/drf-yasg/#history>`__.

So, why use ``drf-yasg2 1.9.4`` instead of ``drf-yasg 1.20``? Because ``drf-yasg 1.20.0`` requires DRF 3.10 or greater and Juniper uses DRF version 3.9.4. 
