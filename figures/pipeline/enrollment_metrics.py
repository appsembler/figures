"""This module collects metrics for a course enrollment (learner/course pair)

# Overview

This is new code for Figures 0.3.10. Its purpose is to address pipeline
performance by reducing calls to `CourseGradeFactory().read.

Calls are reduced by checking if the learner has a `StudentModule` record
modified after the most recent `LearnerCourseGradeMetrics` record `date_for`
field


# Logic

```

for each learner+course  # See bulk_calculate_course_progress_data
    get newest lgcm record
    get newest sm record

    # Check if update needed, see _enrollment_metrics_needs_update
    if not lcgm and not sm
        # Learner has not started course
        skip collection for this learner+course
    else if lcgm and sm
        # we have saved history so we can check to update
        if lcgm.modified is older than sm.modified
            collect new course data  # See _collect_progress_data
            return new metrics object created

    else if not lcgm and sm
        # Learner started course after last collection action
        collect new course data  # See _collect_progress_data
        return new metrics object created

    else  # lcgm and not sm
        # We had collected data previously, but the upstream went away
        # This could happen with data cleansing, like GPPR requests
        # Likely other causes, too
        log condition to figures PipelineError log
        return None
```

# NOTE: We plan to change 'lcgm' in this file to either 'enrollment' or 'LP'
       (for Learner Progress) when an abbreviation is acceptible. This is to get
       this module forward ready for reworking `LearnerCourseGradeMetrics`
"""

from __future__ import absolute_import
from datetime import datetime
from decimal import Decimal
import logging

from django.utils.timezone import utc

from figures.metrics import LearnerCourseGrades
from figures.models import LearnerCourseGradeMetrics
from figures.sites import (get_site_for_course,
                           course_enrollments_for_course,
                           student_modules_for_course_enrollment,
                           UnlinkedCourseError)

logger = logging.getLogger(__name__)


def bulk_calculate_course_progress_data(course_id, date_for=None):
    """Calculates the average progress for a set of course enrollments

    How it works
    1. collects progress percent for each course enrollment
        1.1. If an up to date enrollment metrics record already exists, use that
    2. calculate and return the average of these enrollments

    TODO: Update to filter on active users

    Questions:
    - What makes a learner an active learner?

    """
    progress_percentages = []
    if not date_for:
        date_for = datetime.utcnow().replace(tzinfo=utc).date()

    site = get_site_for_course(course_id)
    if not site:
        raise UnlinkedCourseError('No site found for course "{}"'.format(course_id))

    # We might be able to make this more efficient by finding only the learners
    # in the course with StudentModule (SM) records then get their course
    # enrollment (CE) records as we can ignore any learners without SM records
    # since that means they don't have any course progress
    for ce in course_enrollments_for_course(course_id):
        sm = student_modules_for_course_enrollment(
            site=site,
            course_enrollment=ce).order_by('-modified')
        if sm:
            metrics = collect_metrics_for_enrollment(site=site,
                                                     course_enrollment=ce,
                                                     date_for=date_for,
                                                     student_modules=sm)
            if metrics:
                progress_percentages.append(metrics.progress_percent)

    return dict(
        average_progress=calculate_average_progress(progress_percentages),
    )


def calculate_average_progress(progress_percentages):
    """Calcuates average progress from a list of values

    TODO: How do we want to handle malformed data?
    """
    if progress_percentages:
        average_progress = float(
            sum(progress_percentages)) / float(len(progress_percentages))
        average_progress = float(
            Decimal(average_progress).quantize(Decimal('.00')))
    else:
        average_progress = 0.0
    return average_progress


def collect_metrics_for_enrollment(site, course_enrollment, date_for, student_modules=None):
    """Collect metrics for enrollment (learner+course)

    NOTE: We pass in the student_modules for the learner to save excution time
    However, there is the issue that the caller could pass them in out of proper order
    Therefore we will revisit if we really need to open this up for error or
    if we can accept calling the query twice for the sake of data integrity.

    One compromise is to implement a "most recent sm function in sites"
    Eventually (and maybe sooner rather than later), this concern should go
    away as we move toward live data capture into Figures 'EnrollmentData' and
    the succcessor to LearnerCourseGradeMetrics to snapshot learner progress
    over time (either live capture or frequent scheduled snapshot checks)

    This function performs course enrollment merics collection for the given
    unique enrollment identified by the learner and course. It is initial code
    in refactoring the pipeline for learner progress

    Important models here are:
    * Platform models:
        * CourseEnrollment (CE)
        * StudentModule (SM)
    * Figures models:
        * LearnerCourseGradeMetrics (LCGM)

    # Workflow

    * Get date of most recent StudentModule record, for the enrollment record
    * Get date of most recent LearnerCourseGradeMetrics record, LCGM, for the
      enrollment
    * if LCGM does not exist or SM.modified is more recent than LCGM.modified then
        * collect course_data via CourseEnrollmentFactory().read(...)
        * create new LearnerCourseGradesMetics record with the updated data
        * retain reference to tne new record
    * else return the existing LearnerCourseGradesMetics record if it exists
    * else return None if no existing LearnerCourseGradesMetics record
    """

    # The following are two different ways to avoide the dreaded error
    #     "Instance of 'list' has no 'order_by' member (no-member)"
    # See: https://github.com/PyCQA/pylint-django/issues/165

    if not student_modules:
        student_modules = student_modules_for_course_enrollment(
            site=site,
            course_enrollment=course_enrollment).order_by('-modified')

    # check if there are any StudentModule records for the enrollment
    # if not, no progress to report

    # If there are no student module records, then the learner had no activity
    # in this course, so we return None
    if not student_modules:
        return None

    most_recent_sm = student_modules[0]
    most_recent_lcgm = LearnerCourseGradeMetrics.objects.latest_lcgm(
        user=course_enrollment.user,
        course_id=course_enrollment.course_id)

    if _enrollment_metrics_needs_update(most_recent_lcgm, most_recent_sm):
        progress_data = _collect_progress_data(most_recent_sm)
        # When the pipeline gets interrupted there can be a state where there
        # are LCGM records for the 'date_for'
        # The 'date_for' is is yesterday in normal operation.
        #
        # TODO: Handle this. It can cause an 'IntegrityError' 1062 (a MySQL error)
        # "Duplicate entry '<user_id>-<course_id><date_for>' for key
        # '<table_name>_user_id_<hash>_uniq'"
        metrics = _new_enrollment_metrics_record(site=site,
                                                 course_enrollment=course_enrollment,
                                                 progress_data=progress_data,
                                                 date_for=date_for)
    else:
        metrics = most_recent_lcgm
    return metrics


def _enrollment_metrics_needs_update(most_recent_lcgm, most_recent_sm):
    """Returns True if we need to update our learner progress, False otherwise

    See the #Logic section in this module's docstring

    If we need to check that the records match the same user and course, we
    can do something like:

    ```
    class RecordMismatchError(Exception):
        pass


    def rec_matches_user_and_course(lcgm, sm):
        return lcgm.user == sm.student and lcgm.course_id == sm.course_id
    ```

    And in this function add the check when we have both records:

    ```
        if not rec_matches_user_and_course(most_recent_lcgm, most_recent_sm):
            rec_msg = '{}(user_id={}, course_id="{}"'
            msg1 = rec_msg.format('lcgm',
                                  most_recent_lcgm.user.id,
                                  most_recent_lcgm.course_id)
            msg2 = rec_msg.format('sm',
                                  most_recent_sm.student.id,
                                  most_recent_sm.course_id)
            raise RecordMismatchError(msg1 + ':' + msg2)
    ```
    """
    # First assume we need to update the enrollment metrics record
    needs_update = True
    if not most_recent_lcgm and not most_recent_sm:
        # Learner has not started coursework
        needs_update = False
    elif most_recent_lcgm and most_recent_sm:
        # Learner has past course activity
        needs_update = most_recent_lcgm.date_for < most_recent_sm.modified.date()
    elif not most_recent_lcgm and most_recent_sm:
        # No LCGM recs, so Learner started on course after last collection
        # This could also happen
        # If this is the irst time collection is run for the learner+course
        # if an unhandled error prevents LCGM from saving
        # if the learner's LCGM recs were deleted
        needs_update = True
    elif most_recent_lcgm and not most_recent_sm:
        # This shouldn't happen. We log this state as an error
        # This case is an artifact from before enrollment metrics were reworked.
        # Figures used to collect an LCGM record for every enrollment every day.
        # Now we only create a new LCGM record when there is a new or changed
        # StudentModule record
        # However, this condition will occur until all the "unlinked" LCGM
        # records are deleted
        #
        # We log
        msg = ('FIGURES:PIPELINE:LCGM record exists without StudentModule'
               ' lcgm_id={lcgm_id}, user_id={user_id}, course_id={course_id}')
        logger.warning(msg.format(lcgm_id=most_recent_lcgm.id,
                                  user_id=most_recent_lcgm.user_id,
                                  course_id=most_recent_lcgm.course_id))
        needs_update = False
    return needs_update


def _new_enrollment_metrics_record(site, course_enrollment, progress_data, date_for):
    """Convenience function to save progress metrics to Figures
    """
    return LearnerCourseGradeMetrics.objects.create(
        site=site,
        user=course_enrollment.user,
        course_id=str(course_enrollment.course_id),
        date_for=date_for,
        points_possible=progress_data['points_possible'],
        points_earned=progress_data['points_earned'],
        sections_worked=progress_data['sections_worked'],
        sections_possible=progress_data['count']
        )


def _collect_progress_data(student_module):
    """Get new progress data for the learner/course

    Uses `figures.metrics.LearnerCourseGrades` to retrieve progress data via
    `CourseGradeFactory().read(...)` and calculate progress percentage
    """
    lcg = LearnerCourseGrades(user_id=student_module.student_id,
                              course_id=student_module.course_id)
    course_progress_details = lcg.progress()
    return course_progress_details
