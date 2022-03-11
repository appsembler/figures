"""This module handles enrollments

Enrollment specific functionality should go here unless the functionality would
only be run in the pipeline.

At some point we might make an `Enrollment` class. But for now, this module is
here to build functionality to shed more light into what such a class would
look like.
"""
from figures.compat import StudentModule
from figures.models import EnrollmentData


def student_modules_for_enrollment(enrollment):
    """Return an enrollment's StudentModule records, if they exist

    This function exists because edx-platform does not have a model relationship between
    `CourseEnrollment` and `StudentModule`.
    """
    return StudentModule.objects.filter(student_id=enrollment.user_id,
                                        course_id=enrollment.course_id)


def student_modules_for_enrollment_after_date(enrollment, date_for):
    """Return StudentModule records modified for the enrollment after a date

    TODO: Test if we need to do `modified__gte=next_day(date_for)` or if
    `modified__gt=date_for` will trigger for times after midnight but before
    the next day

    We can ignore `StudentModule.created` because a new record also sets the
    `modified` field.
    """
    return student_modules_for_enrollment(enrollment).filter(modified__gte=date_for)


def is_enrollment_data_out_of_date(enrollment):
    """
    Assumes being called with an enrollment with student modules
    """
    # has EnrollmentData records? if not, then out of date
    edrec = EnrollmentData.objects.get_for_enrollment(enrollment)
    if edrec:
        sm = student_modules_for_enrollment_after_date(enrollment, edrec.date_for)
        # All we care about is if there are student modules modified
        # after the EnrollmentData record was `date_for`
        # out_of_date.append(enrollment)
        out_of_date = True if sm.exists() else False
    else:
        # Just check if there are student modules for the enrollment, ever
        # If there are student modules (and we've already check there is no
        # enrollment), then we need to update
        # If there are no student modules, then the enrollment had no activity
        # then return whether there are StudentModule records or not
        out_of_date = student_modules_for_enrollment(enrollment).exists()

    return out_of_date
