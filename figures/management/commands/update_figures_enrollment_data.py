"""This Django management command updates Figures EnrollmentData records

Running this will trigger figures.tasks.update_enrollment_data for every site
unless the '--site' option is used. Then it will update just that site
"""
from __future__ import print_function
from __future__ import absolute_import
from textwrap import dedent
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from figures.tasks import update_enrollment_data
from figures.sites import get_sites


def get_site(identifier):
    """Quick-n-dirty function to let the caller choose the site id or domain
    Let the 'get' fail if record can't be found from the identifier
    """
    try:
        filter_arg = dict(pk=int(identifier))
    except ValueError:
        filter_arg = dict(domain=identifier)
    return Site.objects.get(**filter_arg)


class Command(BaseCommand):
    """Populate Figures metrics models

    Improvements
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('--no-delay',
                            action='store_true',
                            default=False,
                            help='Disable the celery "delay" directive')
        parser.add_argument('--site',
                            help='backfill a specific site. provide id or domain name')

    def handle(self, *args, **options):
        print('BEGIN: Update Figures EnrollmentData')

        if options['site']:
            sites = [get_site(options['site'])]
        else:
            sites = get_sites()
        for site in sites:
            print('Updating EnrollmentData for site "{}"'.format(site.domain))
            if options['no_delay']:
                update_enrollment_data(site_id=site.id)
            else:
                update_enrollment_data.delay(site_id=site.id)  # pragma: no cover

        print('DONE: Update Figures EnrollmentData')
