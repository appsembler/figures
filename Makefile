#
# Work in progress makefile to simplify Figures development
#

.PHONY: help clean_tests clean_webpack_buld clean_python_build build_python lint pip_install test twine_check twine_push_test

help:
	@echo "Targets:"
	@echo " - clean_tests"
	@echo " - clean_webpack_build"
	@echo " - clean_python_build"
	@echo " - build_python"
	@echo " - coverage"
	@echo " - lint"
	@echo " - pip_install"
	@echo " - test"
	@echo " -twine_check"
	@echo " -twine_push_test"
	@echo " -twine_push_prod"

clean_tests:
	find tests -type f -name "*.pyc" -exec rm -f {} \;
	find figures -type f -name "*.pyc" -exec rm -f {} \;
	find devsite -type f -name "*.pyc" -exec rm -f {} \;
	find tests -type d -name __pycache__ -exec rm -r {} \+
	find devsite -type d -name __pycache__ -exec rm -r {} \+

# Clean the webpack build
clean_webpack_build:
	rm -rf figures/static/figures/*
	rm figures/webpack-stats.json

clean_python_build:
	rm -rf dist
	rm -rf Figures.egg-info

build_python: clean_python_build
	python setup.py sdist bdist_wheel --universal

coverage:
	py.test --cov-report term-missing --cov=figures tests/

lint:
	pylint --load-plugins pylint_django ./figures

pip_install:
	pip install -r devsite/requirements.txt

test: clean
	# We need to have the packages installed in the ./requirements.txt
	# For tests to run. Best to do this in a venv
	py.test


twine_check:
	twine check dist/*

twine_push_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

twine_push_prod:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

