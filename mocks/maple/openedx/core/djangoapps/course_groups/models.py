"""
Copied and modified from openedx.core.djangoapps.course_groups.models
"""

from __future__ import absolute_import
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction


from opaque_keys.edx.django.models import CourseKeyField


class CourseUserGroup(models.Model):
    """
    This model represents groups of users in a course.  Groups may have different types,
    which may be treated specially.  For example, a user can be in at most one cohort per
    course, and cohorts are used to split up the forums by group.
    """
    class Meta(object):
        unique_together = (('name', 'course_id'), )

    name = models.CharField(max_length=255,
                            help_text=("What is the name of this group?  "
                                       "Must be unique within a course."))
    users = models.ManyToManyField(User, db_index=True, related_name='course_groups',
                                   help_text="Who is in this group?")

    # Note: groups associated with particular runs of a course.  E.g. Fall 2012 and Spring
    # 2013 versions of 6.00x will have separate groups.
    course_id = CourseKeyField(
        max_length=255,
        db_index=True,
        help_text="Which course is this group associated with?",
    )

    # For now, only have group type 'cohort', but adding a type field to support
    # things like 'question_discussion', 'friends', 'off-line-class', etc
    COHORT = 'cohort'  # If changing this string, update it in migration 0006.forwards() as well
    GROUP_TYPE_CHOICES = ((COHORT, 'Cohort'),)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES)

    @classmethod
    def create(cls, name, course_id, group_type=COHORT):
        """
        Create a new course user group.

        Args:
            name: Name of group
            course_id: course id
            group_type: group type
        """
        return cls.objects.get_or_create(
            course_id=course_id,
            group_type=group_type,
            name=name
        )

    def __str__(self):
        return self.name


class CohortMembership(models.Model):
    """Used internally to enforce our particular definition of uniqueness"""

    course_user_group = models.ForeignKey(CourseUserGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = CourseKeyField(max_length=255)

    class Meta(object):
        unique_together = (('user', 'course_id'), )

    def clean_fields(self, *args, **kwargs):
        if self.course_id is None:
            self.course_id = self.course_user_group.course_id
        super(CohortMembership, self).clean_fields(*args, **kwargs)

    def clean(self):
        if self.course_user_group.group_type != CourseUserGroup.COHORT:
            raise ValidationError(
                "CohortMembership cannot be used with CourseGroup types other than COHORT")
        if self.course_user_group.course_id != self.course_id:
            raise ValidationError("Non-matching course_ids provided")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean(validate_unique=False)

        return super(CohortMembership, self).save(force_insert=force_insert,
                                                  force_update=force_update,
                                                  using=using,
                                                  update_fields=update_fields)
    '''
    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False)

        # Avoid infinite recursion if creating from get_or_create() call below.
        # This block also allows middleware to use CohortMembership.get_or_create without worrying about outer_atomic
        if 'force_insert' in kwargs and kwargs['force_insert'] is True:
            with transaction.atomic():
                self.course_user_group.users.add(self.user)
                super(CohortMembership, self).save(*args, **kwargs)
            return

        # This block will transactionally commit updates to CohortMembership and underlying course_user_groups.
        # Note the use of outer_atomic, which guarantees that operations are committed to the database on block exit.
        # If called from a view method, that method must be marked with @transaction.non_atomic_requests.
        with outer_atomic(read_committed=True):

            saved_membership, created = CohortMembership.objects.select_for_update().get_or_create(
                user__id=self.user.id,
                course_id=self.course_id,
                defaults={
                    'course_user_group': self.course_user_group,
                    'user': self.user
                }
            )

            # If the membership was newly created, all the validation and course_user_group logic was settled
            # with a call to self.save(force_insert=True), which gets handled above.
            if created:
                return

            if saved_membership.course_user_group == self.course_user_group:
                raise ValueError("User {user_name} already present in cohort {cohort_name}".format(
                    user_name=self.user.username,
                    cohort_name=self.course_user_group.name
                ))
            self.previous_cohort = saved_membership.course_user_group
            self.previous_cohort_name = saved_membership.course_user_group.name
            self.previous_cohort_id = saved_membership.course_user_group.id
            self.previous_cohort.users.remove(self.user)

            saved_membership.course_user_group = self.course_user_group
            self.course_user_group.users.add(self.user)

            super(CohortMembership, saved_membership).save(update_fields=['course_user_group'])
'''
