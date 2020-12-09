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

from django.utils.timezone import utc

from figures.metrics import LearnerCourseGrades
from figures.models import LearnerCourseGradeMetrics, PipelineError
from figures.pipeline.logger import log_error
from figures.sites import (
    get_site_for_course,
    get_student_modules_for_course_in_site,
    course_enrollments_for_course,
    UnlinkedCourseError,
    )


def bulk_calculate_course_progress_data(course_id, date_for=None):
    """Calculates the average progress for a set of course enrollments

    How it works
    1. collects progress percent for each course enrollment
        1.1. If up to date enrollment metrics record already exists, use that
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

    course_sm = get_student_modules_for_course_in_site(site=site,
                                                       course_id=course_id)
    for ce in course_enrollments_for_course(course_id):
        metrics = collect_metrics_for_enrollment(site=site,
                                                 course_enrollment=ce,
                                                 course_sm=course_sm,
                                                 date_for=date_for)
        if metrics:
            progress_percentages.append(metrics.progress_percent)
        else:
            # Log this for troubleshooting
            error_data = dict(
                msg=('Unable to create or retrieve enrollment metrics ' +
                     'for user {} and course {}'.format(ce.user.username,
                                                        str(ce.course_id)))
            )
            log_error(
                error_data=error_data,
                error_type=PipelineError.COURSE_DATA,
                user=ce.user,
                course_id=str(course_id)
            )

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


def collect_metrics_for_enrollment(site, course_enrollment, course_sm, date_for=None):
    """Collect metrics for enrollment (learner+course)

    This function performs course enrollment merics collection for the given
    unique enrollment identified by the learner and course. It is initial code
    in refactoring the pipeline for learner progress

    Important models here are:
    * StudentModule (SM)
    * LearnerCourseGradeMetrics (LCGM)
    * CourseEnrollment (CE)

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
    if not date_for:
        date_for = datetime.utcnow().replace(tzinfo=utc).date()

    # The following are two different ways to avoide the dreaded error
    #     "Instance of 'list' has no 'order_by' member (no-member)"
    # See: https://github.com/PyCQA/pylint-django/issues/165
    student_modules = course_sm.filter(
        student_id=course_enrollment.user.id).order_by('-modified')
    if student_modules:
        most_recent_sm = student_modules[0]
    else:
        most_recent_sm = None

    lcgm = LearnerCourseGradeMetrics.objects.filter(
        user=course_enrollment.user,
        course_id=str(course_enrollment.course_id))
    most_recent_lcgm = lcgm.order_by('date_for').last()

    if _enrollment_metrics_needs_update(most_recent_lcgm, most_recent_sm):
        progress_data = _collect_progress_data(most_recent_sm)
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

        # using 'COURSE_DATA' for the pipeline error type. Although we should
        # revisit logging and error tracking in Figures to define a clear
        # approach that has clear an intuitive contexts for the logging event
        #
        # We neede to decide:
        #
        # 1. Is this always an error state? Could this condition happen naturally?
        #
        # 2. Which error type should be created and what is the most applicable
        #    context
        #    Candidates
        #    - Enrollment (learner+course) context
        #    - Data state context - Why would we have an LCGM
        #
        # So we hold off updating PipelineError error choises initially until
        # we can think carefully on how we tag pipeline errors
        #
        error_data = dict(
            msg='LearnerCourseGradeMetrics record exists without StudentModule',
        )
        log_error(
            error_data=error_data,
            error_type=PipelineError.COURSE_DATA,
            user=most_recent_lcgm.user,
            course_id=str(most_recent_lcgm.course_id)
        )
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
