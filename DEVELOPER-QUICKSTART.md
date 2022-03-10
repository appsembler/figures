# Figures Developer Quickstart Guide

## 1. Overview

This document guides you through getting Figures setup on your development machine.

Requirements are that you have Python 3.5.x installed on your development machine. It is also highly recommended that you install [virtualenv](https://virtualenv.pypa.io/).

## 2. Create a virtualenv

You should use a Python virtualenv to run Figures standalone development mode. This avoids adding packages to the global or user space python instances.

### Resources

Here are links to help guide setting up virtualenv

- https://virtualenv.pypa.io/en/stable/installation/
- https://virtualenv.pypa.io/en/stable/userguide/
- https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv

## 3. Clone Figures, install dependencies, and test

On your development machine, open a terminal (command line shell) and create or navigate to the directory for which you want to install Figures. This will be the parent directory for your Figures project. Example:

**These instructions assume you are running a Python virtualenv**

In the terminal, run the following:

```
git clone https://github.com/appsembler/figures.git
cd figures
pip install -r devsite/requirements/community.txt
```

now we'll run [pytest](https://docs.pytest.org/) to make sure that the tests pass:

```
pytest
```

## 4. Build front end assets

Figures front end assets need to be build from the front end sources. Make sure you have (Yarn)[https://yarnpkg.com/lang/en/] installed. Then do the following:

Navigate to the `figures/frontend` directory.

Then download JavaScript dependencies:

```
yarn
```

Then compile Figures front end assets:

```
yarn build
```

## 5. Set up Figures standalone server

Navigate to your Figures workspace (you will be here if you just completed the previous step)

Run the following:

```
cd devsite
./manage.py migrate
```

Next, create a superuser. We'll use this account to log into the development site

```
./manage.py createsuperuser
```

Next, seed the devsite database with mock data. Run the following:

```
./manage.py seed_data
```

The `seed_data` command populates the dev server with mock data then builds metrics on the mock data, backfilling historical data (experimental feature)

## 6. Starting Figures devsite

Navigate to your Figures workspace (you will be here if you just completed the previous step)

Run the following:

```
./manage.py runserver
```

This will start the Django development server on `http://127.0.0.1:8000/`

When you open your browser to the above address, you will see the development server homepage.

There's nothing impressive about it. But you will see a login form.

Enter the credentials you used to create the superuser in step 4.

Now you can click on the Figures link on the page to go to the Figures dashboard.

## 7. Navigating around Figures

_Section incomplete_

Pages of interest:

- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/figures/
- http://127.0.0.1:8000/figures/api/
- http://127.0.0.1:8000/admin/figures/

## 8. Running the pipeline manually

The Figures pipeline will automatically run once a day in a running Open edX Hawthorn instance. The default time os 02:00 UTC and can be configured in the server vars (`lms.env.json`).

You can also run the pipeline manually with the Django management command provided with Figures. This command is `populate_figures_metrics`. You will see options if you run `./management.py populate_figures_metrics --help`

Make sure you have your development virtualenv running. Then navigate to the `devsite` directory and run the following:

```
./manage.py populate_figures_metrics --no-delay
```

This will run the pipeline immediately instead of being queued to celery.

_NOTE_ The above is just for running the pipeline in Figures standalone mode with the included devsite. If you are working with Figures in Open edX (either devstack or fullstack), run the following:

```
./manage.py lms populate_figures_metrics --no-delay
```

## 9. Building the front end assets

You will need yarn installed.

Go to the `frontend` directory and run `yarn`. This will install dependencies

Run `yarn build` to compile the front end assets.

## 10. Running the frontend Webpack server

_TODO: Add this section_

## 11. Installing Figures on Hawthorn Docker Devstack

_TODO: Add this section_
