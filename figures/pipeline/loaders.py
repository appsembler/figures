"""

"""

from __future__ import absolute_import
from figures.models import LearnerCourseGradeMetrics


def save_learner_course_grades(site, date_for, course_enrollment, course_progress_details):
    """

    ``course_progress_details`` data are the ``course_progress_details`` from the
    ``LearnerCourseGrades.course_progress method``

    """
    # details = course_progress['course_progress_details']
    data = dict(
        points_possible=course_progress_details['points_possible'],
        points_earned=course_progress_details['points_earned'],
        sections_worked=course_progress_details['sections_worked'],
        sections_possible=course_progress_details['count']
        )
    obj, created = LearnerCourseGradeMetrics.objects.update_or_create(
        site=site,
        user=course_enrollment.user,
        course_id=str(course_enrollment.course_id),
        date_for=date_for,
        defaults=data)
    return obj, created
