"""This command serves to run system checks for Figures devsite

Initially, this is a convenience command to check that Celery on devsite works
properly

It calls the task `devsite.celery.run_celery_check`

"""

from __future__ import absolute_import
from __future__ import print_function
from django.core.management.base import BaseCommand

from devsite.celery import celery_check


class Command(BaseCommand):

    def run_devsite_celery_task(self):
        """Perform basic Celery checking

        In production, we typically don't want to call `.get()`, but trying it
        here just to see if the results backend is configured and working

        See the `get` method here:
            https://docs.celeryproject.org/en/stable/reference/celery.result.html
        """
        print('Checking Celery...')
        msg = 'run_devsite_check management command'
        result = celery_check.delay(msg)
        print(('Task called. task_id={}'.format(result.task_id)))

        try:
            print(('result={}'.format(result.get())))
        except NotImplementedError as e:
            print(('Error: {}'.format(e)))

        print('Done checking Celery')

    def add_arguments(self, parser):
        """Stub"""
        pass

    def handle(self, *args, **options):
        print('Figures devsite system check.')
        self.run_devsite_celery_task()
        print('Done.')
