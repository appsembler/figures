'''Provides edx-platform functionality for Figures tests

Provides Opaque key derived classes to support edx-platform mocks that use
CourseKeyField objects 

This is to make sure that course key related type errors are trapped in 
figures tests::

    "course-v1:MyOrg EdX101 2015_Spring" is not an instance of 
    <class 'opaque_keys.edx.keys.CourseKey'>


Code copied and modified as needed from:

https://github.com/edx/edx-platform/blob/open-release/ginkgo.master/openedx/core/djangoapps/xmodule_django/models.py

'''

from __future__ import absolute_import
from django.db import models
from opaque_keys.edx.keys import CourseKey
import six

def _strip_object(key):
    """
    Strips branch and version info if the given key supports those attributes.
    """
    if hasattr(key, 'version_agnostic') and hasattr(key, 'for_branch'):
        return key.for_branch(None).version_agnostic()
    else:
        return key


def _strip_value(value, lookup='exact'):
    """
    Helper function to remove the branch and version information from the given value,
    which could be a single object or a list.
    """
    if lookup == 'in':
        stripped_value = [_strip_object(el) for el in value]
    else:
        stripped_value = _strip_object(value)
    return stripped_value


class OpaqueKeyField(six.with_metaclass(models.SubfieldBase, models.CharField)):
    """
    A django field for storing OpaqueKeys.

    The baseclass will return the value from the database as a string, rather than an instance
    of an OpaqueKey, leaving the application to determine which key subtype to parse the string
    as.

    Subclasses must specify a KEY_CLASS attribute, in which case the field will use :meth:`from_string`
    to parse the key string, and will return an instance of KEY_CLASS.
    """
    description = "An OpaqueKey object, saved to the DB in the form of a string."

    Empty = object()
    KEY_CLASS = None

    def __init__(self, *args, **kwargs):
        if self.KEY_CLASS is None:
            raise ValueError('Must specify KEY_CLASS in OpaqueKeyField subclasses')

        super(OpaqueKeyField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is self.Empty or value is None:
            return None

        assert isinstance(value, (six.string_types, self.KEY_CLASS)), \
            "%s is not an instance of basestring or %s" % (value, self.KEY_CLASS)
        if value == '':
            # handle empty string for models being created w/o fields populated
            return None

        if isinstance(value, six.string_types):
            if value.endswith('\n'):
                # An opaque key with a trailing newline has leaked into the DB.
                # Log and strip the value.
                log.warning(u'{}:{}:{}:to_python: Invalid key: {}. Removing trailing newline.'.format(
                    self.model._meta.db_table,  # pylint: disable=protected-access
                    self.name,
                    self.KEY_CLASS.__name__,
                    repr(value)
                ))
                value = value.rstrip()
            return self.KEY_CLASS.from_string(value)
        else:
            return value

    def get_prep_lookup(self, lookup, value):
        if lookup == 'isnull':
            raise TypeError('Use {0}.Empty rather than None to query for a missing {0}'.format(self.__class__.__name__))

        return super(OpaqueKeyField, self).get_prep_lookup(
            lookup,
            # strip key before comparing
            _strip_value(value, lookup)
        )

    def get_prep_value(self, value):
        if value is self.Empty or value is None:
            return ''  # CharFields should use '' as their empty value, rather than None

        # HACK: Remarking out the assertion until we can investigate why
        # the value is sometimes unicode and sometimes an OpaqueKey/CourseLocator
        #assert isinstance(value, self.KEY_CLASS), "%s is not an instance of %s" % (value, self.KEY_CLASS)
        serialized_key = six.text_type(_strip_value(value))
        if serialized_key.endswith('\n'):
            # An opaque key object serialized to a string with a trailing newline.
            # Log the value - but do not modify it.
            log.warning(u'{}:{}:{}:get_prep_value: Invalid key: {}.'.format(
                self.model._meta.db_table,  # pylint: disable=protected-access
                self.name,
                self.KEY_CLASS.__name__,
                repr(serialized_key)
            ))
        return serialized_key

    def validate(self, value, model_instance):
        """Validate Empty values, otherwise defer to the parent"""
        # raise validation error if the use of this field says it can't be blank but it is
        if not self.blank and value is self.Empty:
            raise ValidationError(self.error_messages['blank'])
        else:
            return super(OpaqueKeyField, self).validate(value, model_instance)

    def run_validators(self, value):
        """Validate Empty values, otherwise defer to the parent"""
        if value is self.Empty:
            return

        return super(OpaqueKeyField, self).run_validators(value)


class CourseKeyField(OpaqueKeyField):
    """
    A django Field that stores a CourseKey object as a string.
    """
    description = "A CourseKey object, saved to the DB in the form of a string"
    KEY_CLASS = CourseKey
