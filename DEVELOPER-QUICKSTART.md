
# Figures Developer Quickstart Guide

## 1. Overview

This document guides you through getting Figures setup on your development machine.

Requirements are that you have Python 2.7.x installed on your development machine. Hawthorn devstack uses 2.7.12. It is also highly recommended that you install `[virtualenv]()`

## 2. Create a virtualenv

_TODO: cleanup this section_

You should use a Python virtualenv to run Figures standalone development mode. This avoids adding packages to the global or user space python instances.

### Resources

Here are links to help guide setting up virtualenv

* https://virtualenv.pypa.io/en/stable/installation/
* https://virtualenv.pypa.io/en/stable/userguide/
* https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv

## 3. Clone Figures, install dependencies, and test

On your development machine, open a terminal (command line shell) and create or navigate to the directory for which you want to install Figures. This will be the parent directory for your Figures project. Example:

**These instructions assume you are running a Python virtualenv**

If you want to use the development branch, substitute `hawthorn-upgrade` for `hawthorn-prerelease`

`hawthorn-upgrade` is the live development branch to support Hawthorn.

In the terminal, run the following:

```
git clone -b hawthorn-prerelease https://github.com/appsembler/figures.git
cd figures
pip install -r devsite/requirements/hawthorn.txt
```

now we'll run [pytest](https://docs.pytest.org/) to make sure that the tests pass:

```
pytest
```


## 4. Setup Figures standalone server

Navigate to your Figures workspace (you will be here if you just completed the previous step)

Run the following:

```
cd devsite
./manage.py migrate
./manage.py createsuperuser
./manage.py seed_data
```

The `seed_data` command populates the dev server with mock data then builds metrics on the mock data, backfilling historical data (experimental feature)

## 5. Starting Figures devsite

Navigate to your Figures workspace (you will be here if you just completed the previous step)

Run the following:

```
./manage.py runserver
```

This will start the Django development server on `http://127.0.0.1:8000/`

When you open your browser to the above address, you will see the development server homepage.

There's nothing impressive about it. But you will see a login form.

Enter the credentials you used to create the superuser in step 4

Now you can click on the Figures link 


## 6. Navigating around

_Section incomplete_

Pages of interest:

* http://127.0.0.1:8000/figures/
* http://127.0.0.1:8000/figures/api/
* http://127.0.0.1:8000/admin/figures/

## 7. Running the pipeline manually

_Section incomplete_


## 8. Building the front end

_Section incomplete_

The frontend assets come pre-built for the Hawthorn prerelease. If you modify the front end code


_TODO: provide example of adding custom layout settings_


From your project root, `cd frontend`

npm install


## 7. Running the frontend in de



