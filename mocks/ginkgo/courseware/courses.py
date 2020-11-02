'''

./common/lib/xmodule/xmodule/modulestore
'''

from __future__ import absolute_import
from django.http import Http404
from xmodule.modulestore.django import modulestore
import six


def get_course_by_id(course_key, depth=0):
    """
    Given a course id, return the corresponding course descriptor.

    If such a course does not exist, raises a 404.

    depth: The number of levels of children for the modulestore to cache. None means infinite depth
    """
    with modulestore().bulk_operations(course_key):
        course = modulestore().get_course(course_key, depth=depth)

    if course:
        return course
    else:
        raise Http404("Course not found: {}.".format(six.text_type(course_key)))
