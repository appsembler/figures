
# Figures Developer Quickstart Guide

## Overview

This document guides you through getting Figures setup on your development machine.

Requirements are that you have Python 2.7.x installed on your development machine. Hawthorn devstack uses 2.7.12. It is also highly recommended that you install `[virtualenv]()`

## Clone Figures

```
git clone -b hawthorn-prerelease https://github.com/appsembler/figures.git
```


If you want to use the development branch:

```
git clone -b hawthorn-upgrade https://github.com/appsembler/figures.git
```

This is the live development branch to support Hawthorn


## Create a virtualenv

_TODO: cleanup this section_

You should use a Python virtualenv to run Figures standalone development mode. This avoids adding packages to the global or user space python instances.

### Resources

Here are links to help guide setting up virtualenv

* https://virtualenv.pypa.io/en/stable/installation/
* https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv


## Install dependencies

Enable your virtualenv

From your project root folder, run:

pip install -r devsite/requirements/hawthorn.txt

## Setup Figures standalone server

cd devsite
./manage.py migrate
./manage.py createsuperuser
./manage.py seed_data

## Starting Figures devsite

./manage.py runserver

This will start the Django development server on `http://localhost:8000`


## Building the front end

The frontend assets come pre-built for the Hawthorn prerelease. If you modify the front end code


From your project root, `cd frontend`

npm install


## Running the frontend in de



