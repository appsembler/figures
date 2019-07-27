#
# Work in progress makefile to simplify Figures development
#

.PHONY: help clean_tests clean_webpack_buld clean_python_build build_python lint pip_install test twine_check twine_push_test delete_mock_migrations reset_mock_migrations

help:
	@echo "Targets:"
	@echo " - clean_python"
	@echo " - clean_python_build"
	@echo " - clean_webpack_build"
	@echo " - build_python"
	@echo " - coverage"
	@echo " - lint"
	@echo " - pip_install"
	@echo " - test"
	@echo " - twine_check"
	@echo " - twine_push_test"
	@echo " - twine_push_prod"
	@echo " - delete_mock_migrations"
	@echo " - update_mock_migrations"

clean_python:
	find tests -type f -name "*.pyc" -exec rm -f {} \;
	find figures -type f -name "*.pyc" -exec rm -f {} \;
	find devsite -type f -name "*.pyc" -exec rm -f {} \;
	find tests -type d -name __pycache__ -exec rm -r {} \+
	find devsite -type d -name __pycache__ -exec rm -r {} \+

# Clean the Python dist build
clean_python_build:
	rm -rf dist
	rm -rf Figures.egg-info

# Clean the webpack build
clean_webpack_build:
	rm -rf figures/static/figures/*
	rm figures/webpack-stats.json

build_python: clean_python_build
	python setup.py sdist bdist_wheel --universal

coverage:
	py.test --cov-report term-missing --cov=figures tests/

lint:
	pylint --load-plugins pylint_django ./figures

pip_install:
	pip install -r devsite/requirements/hawthorn.txt

test: clean_python
	# We need to have the packages installed in the ./requirements.txt
	# For tests to run. Best to do this in a venv
	py.test

twine_check:
	twine check dist/*

twine_push_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

twine_push_prod:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

delete_mock_migrations:
	# Run this if you need to delete existing tests mock migrations
	# You might need to do this to address migration dependency issues
	find tests/mocks -type f -path "*/migrations/0001_initial.py" -print -exec rm -f {} \;

update_mock_migrations:
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

