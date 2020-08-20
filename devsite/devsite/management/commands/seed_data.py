"""
This command writes synthetic data to the metrics models. Any existing data are deleted
"""

from __future__ import absolute_import
from __future__ import print_function
from django.core.management.base import BaseCommand

from devsite import seed


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('Seeding mock data for Figures demo')
        seed.wipe()
        seed.seed_all()
        print('Done.')
