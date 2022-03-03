"""This module updates Figures enrollment data and calculates aggregate progress

* It updates `EnrollmentData` and `LearnerCourseGradeMetrics` records
* It calculate course progress from EnrollmentData records

This generates the same metrics as the original enrollment_metrics modules,
but does it differently.

## How it differs from the previous version

This module improves on the existing enrollment metrics collection module,
`figures.pipeline.enrollment_metrics`

* It separates the activities to create and update Figures per-enrollment data
  collected
* This separation lets Figures run metrics in distinct stages
    * First, collect per-enrollment data
    * Second, aggregate metrics based on collected data
* This provides a workflow that is easier to resume if interrupted
* This provides workflow that is simpler to debug
* This simplifies and speeds up aggregate progress metrics, collapsing complex
  code into a single Django queryset aggregation
* This update lays groundwork for further metrics improvements and enhancements
  such as metrics on subsets of learners in a course or progress of subsets of
  learners across courses

# Developer Notes

This module provides

"""
from django.db.models import Avg
from figures.course import Course
from figures.helpers import utc_yesterday
from figures.models import EnrollmentData
from figures.sites import UnlinkedCourseError


def update_enrollment_data_for_course(course_id):
    """Updates Figures per-enrollment data for enrollments in the course
    Checks for and creates new `LearnerCourseGradeMetrics` records and updates
    `EnrollmentData` records

    Return results are a list of the results returned by `update_enrollment_data`
    """
    date_for = utc_yesterday()
    the_course = Course(course_id)
    if not the_course.site:
        raise UnlinkedCourseError('No site found for course "{}"'.format(course_id))

    # Any updated student module records? if so, then get the unique enrollments
    # for each enrollment, check if LGCM is out of date or up to date
    active_enrollments = the_course.enrollments_active_on_date(date_for)
    return [EnrollmentData.objects.update_metrics(the_course.site, ce)
            for ce in active_enrollments]


def calculate_course_progress(course_id):
    """Return average progress percentage for all enrollments in the course
    """
    results = EnrollmentData.objects.filter(course_id=str(course_id)).aggregate(
        average_progress=Avg('progress_percent'))

    # This is a bit of a hack. When we overhaul progress data, we should really
    # have None for progress if there's no data. But check how SQL AVG performs
    if results['average_progress'] is None:
        results['average_progress'] = 0.0
    return results
