#
# Makefile to simplify Figures development
#

include .env*
export $(shell sed 's/=.*//' .env*)

SHELL := /bin/bash
.PHONY: help


help: ## This help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | \
		sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

environment.display:  ## Prints the environment values used in this makefile as defined in .env.* files
	@echo EDX_PLATFORM_RELEASE = $(EDX_PLATFORM_RELEASE)


##
## Python targets
##

python.clean:  ## Removes generated Python bytecode files
	@echo Removing generated Python bytecode files...
	find tests -type f -name "*.pyc" -exec rm -f {} \;
	find figures -type f -name "*.pyc" -exec rm -f {} \;
	find devsite -type f -name "*.pyc" -exec rm -f {} \;
	find mocks -type f -name "*.pyc" -exec rm -f {} \;
	find tests -type d -name __pycache__ -exec rm -r {} \+
	find figures -type d -name __pycache__ -exec rm -r {} \+
	find devsite -type d -name __pycache__ -exec rm -r {} \+
	find mocks -type d -name __pycache__ -exec rm -r {} \+
	find . -type d -name .pytest_cache -exec rm -r {} \+

# Clean the Python dist build
python.build.clean:  ## Removes Python packaging build files
	rm -rf dist
	rm -rf Figures.egg-info

pip.install:   ## Install Appsembler Hawthorn requirements for devsite
	pip install -r devsite/requirements/hawthorn_appsembler.txt


python.build:   python.build.clean  ## Build Python package
	python setup.py sdist bdist_wheel --universal


pylint:  ## lint
	pylint --load-plugins pylint_django ./figures

coverage:  ## Run coverage, without the built-in virtualenv
	coverage run --source figures -m py.test; coverage report -m

ginkgo.pytest:  ## Run Pytest for the Ginkgo environment
	OPENEDX_RELEASE=GINKGO pytest -c pytest-ginkgo.ini

ginkgo.tox:  ## Run tox just for the Ginkgo environment
	tox -e py27-ginkgo

juniper.pytest:  ## Run Pytest for the Juniper environment
	OPENEDX_RELEASE=JUNIPER pytest -c pytest-juniper.ini

### Devsite Docker targets

devsite.docker.prep: ## state needed to run devsite docker
	pip install -e .

devsite.docker.up: devsite.docker.prep  ## Start devsite docker
	cd devsite; docker-compose up

devsite.docker.rabbitmq.config:  ## configure RabbitMQ container
	cd devsite; docker cp rabbitmq-init.sh devsite_rabbitmq_figures_1:/rabbitmq-init.sh ; \
		docker exec devsite_rabbitmq_figures_1 /rabbitmq-init.sh

devsite.docker.celery.start:  ## Start the celery server
	cd devsite; celery -A devsite worker --logleve=info

### Automatically constructed Virtualenv based targets

ve/bin/figures-ws: devsite/requirements/${EDX_PLATFORM_RELEASE}_appsembler.txt
	@echo Installing Figures workspace test and build project requirements...
	@virtualenv ve
	@ve/bin/pip install -r devsite/requirements/${EDX_PLATFORM_RELEASE}_appsembler.txt

ve.clean:  ## Clean and rebuilt the built-in virtualenv
	@echo Flush workspace venv...
	@rm -rf ve
	@make ve/bin/figures-ws

ve.coverage: ve/bin/figures-ws  ## coverage with the built-invirtualenv
	@. ve/bin/activate; coverage run --source figures -m py.test; coverage report -m

ve.test: python.clean ve/bin/figures-ws ## Run pytest using the built-in virtualenv
	# We need to have the packages installed in the ./requirements.txt
	# For tests to run. Best to do this in a venv
	@. ve/bin/activate; py.test


##
## Experimental targets
##
## These targets are a work in progress

mocks.hawthorn.migrations.delete:  ## Delete migrations for Hawthorn mocks
	# Run this if you need to delete existing tests mock migrations
	# You might need to do this to address migration dependency issues
	find mocks/hawthorn -type f -path "*/migrations/0001_initial.py" -print -exec rm -f {} \;

mocks.hawthorn.migrations.update:  ## Update migrations for Hawthorn mocks
	# Run this command if you want to update mock migrations
	# You likely need to do this if you change model fields in the mocks
	# NOTE: Apps are explicity identified in this make target
	# Only apps with models need to be included
	# If you get an error running this, then try deleting existing mock migrations first
	cd devsite && \
	./manage.py makemigrations certificates && \
	./manage.py makemigrations courseware && \
	./manage.py makemigrations course_overviews && \
	./manage.py makemigrations student

##
## PyPI deployment targets
##

twine.check:  ## Check twine build
	twine check dist/*

twine.push.test:  ## Push build to PyPi test server
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

twine.push.prod:  ## Push build to PyPI production server
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

##
## Frontend targets
##

frontend.build.clean:  ## Clean the webpack build
	rm -rf figures/static/figures/*
	rm figures/webpack-stats.json

frontend.build: frontend.build.clean  ## Yarn build frontend assets
	cd frontend; yarn build
