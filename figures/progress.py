"""
This module exists as a quick fix to prevent cyclical dependencies
"""
from figures.compat import (
    chapter_grade_values,
    course_grade_from_course_id
)


class EnrollmentProgress(object):
    """
    Quick hack class adapted from LearnerCourseGrades. Purpose is encapsulating
    logic we need to get the total sections and points of a course.

    The proper fix is to have an API to query the course structure and cache
    those data into a Figures "CourseData" type model to get course level data
    like "sections_possible" and "points_possible" Non-learner specific course
    data.

    But until we do that, doing a stripped down version of LearnerCourseGrades
    that does fewer operations to get to a learner's progress (grades) data

    TODO: After our performance improvement rollout, rework this functionality.
    Perhaps rework this class as a convenience wrapper around the platform's
    'course_grade' structure, then get rid of metrics.LearnerCourseGrades
    """
    def __init__(self, user, course_id, **_kwargs):
        """
        If figures.compat.course_grade is unable to retrieve the course blocks,
        it raises:

            django.core.exceptions.PermissionDenied(
                "User does not have access to this course")
        """
        self.course_grade = course_grade_from_course_id(learner=user,
                                                        course_id=course_id)
        self.progress = self._get_progress()

    # Can be a class method instead of instance
    def is_section_graded(self, section):
        # just being defensive, might not need to check if
        # all_total exists and if all_total.possible exists
        return bool(
            hasattr(section, 'all_total')
            and hasattr(section.all_total, 'possible')
            and section.all_total.possible > 0
        )

    def sections(self, only_graded=False, **_kwargs):
        """
        yields objects of type:
            lms.djangoapps.grades.new.subsection_grade.SubsectionGrade

        Compatibility:

        In Ficus, at least in the default devstack data, chapter_grades is a list
        of dicts
        """

        for chapter_grade in chapter_grade_values(self.course_grade.chapter_grades):
            for section in chapter_grade['sections']:
                if not only_graded or (only_graded and self.is_section_graded(section)):
                    yield section

    def is_completed(self):
        return self.progress['sections_worked'] > 0 and \
            self.progress['sections_worked'] == self.progress['sections_possible']

    def progress_percent(self):
        if self.progress['sections_possible'] > 0:
            return float(self.progress['sections_worked']) / float(
                self.progress['sections_possible'])
        else:
            return 0.0

    def _get_progress(self):
        """
        TODO: FIGURE THIS OUT
        There are two ways we can go about measurig progress:

        The percentage grade points toward the total grade points
        OR
        the number of sections completed toward the total number of sections
        """
        sections_possible = points_possible = points_earned = sections_worked = 0

        for section in self.sections(only_graded=True):
            if section.all_total.earned > 0:
                sections_worked += 1
                points_earned += section.all_total.earned
            sections_possible += 1
            points_possible += section.all_total.possible

        # How about a named tuple instead?
        return dict(
            points_possible=points_possible,
            points_earned=points_earned,
            sections_worked=sections_worked,
            sections_possible=sections_possible,
        )
