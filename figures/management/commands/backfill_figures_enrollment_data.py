"""This Django management command updates Figures EnrollmentData records

Running this will trigger figures.tasks.backfill_enrollment_data_for_course

Specific sites or courses need to be identified. Running without either of these
parameters will raise a CommandError stating that one of these parameters are
needed.

This Django management command does not default to running update on every
enrollment because that could trigger a heavy and long load for larger deployments
that require many EnrollmentData records to be updated.

To specify sites, use the `--sites` parameter, followed by a space delimited list
of domain names. Example:

```
backfill_figures_enrollment_data --sites heres-a-site.com another-site.com
```

To specify courses, use the `--courses` paramter, followed by a space delimited
list of course id string. Example:


### Important

* The above do not include the full Django management command
* These are run for the LMS instance

Either `--sites` or `--courses` parameter needs to be

unless the '--site' option is used. Then it will update just that site

For potential improvements to this management command, see here:

* https://github.com/appsembler/figures/issues/435
"""
from __future__ import print_function
from __future__ import absolute_import

from textwrap import dedent
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from figures.compat import CourseOverview
from figures.helpers import as_course_key
from figures.sites import site_course_ids
from figures.tasks import backfill_enrollment_data_for_course


class Command(BaseCommand):
    """Backfill Figures EnrollmentData model.

    This Django managmenet command provides a basic CLI to create and update
    Figures `EnrollmentData` records.

    It filters on either sites or course ids. Because this is potentially a
    resource intensive command, it requires identifying specific sites or
    course ids. Yes, there's improvement for this.

    * If both sites and courses parameters are used, the sites are ignored
    * If there are any invalid site names or primary keys, the command will fail
      with the Django model's `DoesNotExist` exception
    * If there are any invalid course ids the command will fail with
      `DoesNotExist` if the course id has a valid structure but the course is
      not found and with `InvalidKeyErro` if the course id does not have a valid
      structure (CourseKey.from_string(course_id) fails)

    For potential improvements, read (and contribute if you want) here:

    * https://github.com/appsembler/figures/issues/435
    """
    help = dedent(__doc__).strip()

    def get_sites(self, options):
        """Returns a list of Site objects

        Raises `DoesNotExist` if a site in the list is missing
        If no sites are specified, returns an empty list
        """
        sites = []
        for site_identifier in options.get('sites', []):
            sites.append(Site.objects.get(domain=site_identifier))
        return set(sites)

    def get_course_ids(self, options):
        """Return a validated list of course id strings.

        If no courses are specified, returns an empty list

        Raises `DoesNotExist` or `InvalidKeyError` exceptions if a course id
        is either malformed or is not malformed, but does not exist
        """
        course_ids = []
        for cid_str in options.get('courses', []):
            course_overview = CourseOverview.objects.get(id=as_course_key(cid_str))
            # we got a course overview object. Otherwise, we'd fail here with
            # `InvalidKeyError` or `DoesNotExist` error
            # While we could just use `cid_str`, this has us use the object
            # returned. We do NOT want to check if the key exists because we
            # want to let the user know there was a problem with a course id
            course_ids.append(str(course_overview.id))
        return course_ids

    def update_enrollments(self, course_ids, use_celery=True):
        for course_id in course_ids:
            if use_celery:
                # Call the Celery task with delay
                backfill_enrollment_data_for_course.delay(str(course_id))
            else:
                # Call the Celery task immediately
                backfill_enrollment_data_for_course(str(course_id))

    def add_arguments(self, parser):
        """

        If site domain or id or set of ides are provided, but no course or
        courses provided, runs for all courses in the site

        If a course id or list of course ids provided, processes those courses
        If a site
        """
        parser.add_argument('--sites',
                            nargs='+',
                            default=[],
                            help='backfill a specific site. provide id or domain name')
        parser.add_argument('--courses',
                            nargs='+',
                            default=[],
                            help='backfill a specific course. provide course id string')
        parser.add_argument('--use-celery',
                            action='store_true',
                            default=True,
                            help='Run with Celery worker. Set to false to run in app space ')

    def handle(self, *args, **options):
        print('BEGIN: Backfill Figures EnrollmentData')
        sites = self.get_sites(options)
        course_ids = self.get_course_ids(options)
        use_celery = options['use_celery']

        # Would it benefit to implement a generator method to yield the course id?
        if course_ids:
            self.update_enrollments(course_ids, use_celery=use_celery)

        elif sites:
            for site in sites:
                course_ids = site_course_ids(site)
                self.update_enrollments(course_ids, use_celery=use_celery)

        else:
            raise CommandError('You need to provide at least one site or course to update')

        print('DONE: Backfill Figures EnrollmentData')
