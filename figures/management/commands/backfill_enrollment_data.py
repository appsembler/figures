"""This Django management command updates Figures EnrollmentData records

Running this will trigger figures.tasks.update_enrollment_data for every site
unless the '--site' option is used. Then it will update just that site
"""
from __future__ import print_function
from __future__ import absolute_import
from textwrap import dedent

from figures.tasks import update_enrollment_data

from . import BaseBackfillCommand


class Command(BaseBackfillCommand):
    """Backfill Figures EnrollmentData model.
    """
    help = dedent(__doc__).strip()

    def handle(self, *args, **options):
        print('BEGIN: Backfill Figures EnrollmentData')

        for site in self.get_sites(options['site']):
            print('Updating EnrollmentData for site "{}"'.format(site.domain))
            if options['no_delay']:
                update_enrollment_data(site_id=site.id)
            else:
                update_enrollment_data.delay(site_id=site.id)  # pragma: no cover

        print('DONE: Backfill Figures EnrollmentData')
