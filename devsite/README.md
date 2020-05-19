# Figures Devsite


## Overview

This doc is a work in progress. Key details should exist, but needs fleshing out
for readability and completeness


## Status

Figures devsite Celery support is in its initial phase. Devsite can now run
Figures tasks asynchronously

## Pipeline Sandbox

Figures devsite has an option to run Celery tasks in devsite.


### Requirements / Prerequisites

Docker needs to be installed in your development environment

### Setup and Configuration

Note: This is a WIP

We run the celery worker from the `figures/devsite` directory. It needs to discover Figures.

Install Figures in the devsite venv:

From the Figures project root directory, run:

```
pip install -e figures
```


* Start Docker on your development machine

Go to the `figures/devsite` directory and from the shell, run `docker-compose up`

This will launch the docker container and show console output

In another shell, go to the `figures/devsite` directory and run

```
docker cp rabbitmq-init.sh devsite_rabbitmq_figures_1:/rabbitmq-init.sh
```

See the [docker cp](https://docs.docker.com/engine/reference/commandline/cp/) CLI documentation.


Run the following script to configure the Figures environment in RabbitMQ

```
docker exec devsite_rabbitmq_figures_1 /rabbitmq-init.sh
```

See the [docker exec](https://docs.docker.com/engine/reference/commandline/exec/) CLI documentation.

Note: you can shell into the docker container with the following:

```
docker exec -ti devsite_rabbitmq_figures_1 /bin/bash
```

Update Figures devsite:


```
./manage.py createcachetable
./manage.py migrate django_celery_results
Operations to perform:
  Apply all migrations: django_celery_results
Running migrations:
  Applying django_celery_results.0001_initial... OK
  Applying django_celery_results.0002_add_task_name_args_kwargs... OK
  Applying django_celery_results.0003_auto_20181106_1101... OK
  Applying django_celery_results.0004_auto_20190516_0412... OK
  Applying django_celery_results.0005_taskresult_worker... OK
  Applying django_celery_results.0006_taskresult_date_created... OK
  Applying django_celery_results.0007_remove_taskresult_hidden... OK
```


From the `figures/devsite` directory:

```
celery -A devsite worker --logleve=info
```

# Testing and Exploring

In `figures/devsite`, run `./manage.py devsite_check`


# References

## Celery Results

* https://github.com/celery/django-celery-results
* https://stackoverflow.com/questions/26934522/celery-result-get-not-working
