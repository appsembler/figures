
from __future__ import absolute_import
from rest_framework import serializers

# ReadOnlyFieldSerialzerMixin is from
# openedx.core.djangoapps.user_api.serializers

class ReadOnlyFieldsSerializerMixin(object):
    """
    Mixin for use with Serializers that provides a method
    `get_read_only_fields`, which returns a tuple of all read-only
    fields on the Serializer.
    """
    @classmethod
    def get_read_only_fields(cls):
        """
        Return all fields on this Serializer class which are read-only.
        Expects sub-classes implement Meta.explicit_read_only_fields,
        which is a tuple declaring read-only fields which were declared
        explicitly and thus could not be added to the usual
        cls.Meta.read_only_fields tuple.
        """
        return getattr(cls.Meta, 'read_only_fields', '') + getattr(cls.Meta, 'explicit_read_only_fields', '')

    @classmethod
    def get_writeable_fields(cls):
        """
        Return all fields on this serializer that are writeable.
        """
        all_fields = getattr(cls.Meta, 'fields', tuple())
        return tuple(set(all_fields) - set(cls.get_read_only_fields()))


class AccountLegacyProfileSerializer(serializers.HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):

    @staticmethod
    def get_profile_image(user_profile, user, request=None):
        '''
        For the mock, we probably can get by with just returning dummy data
        '''
        return dict(
            image_url_full= "http://localhost:8000/static/images/profiles/default_500.png",
            image_url_large="http://localhost:8000/static/images/profiles/default_120.png",
            image_url_medium="http://localhost:8000/static/images/profiles/default_50.png",
            image_url_small="http://localhost:8000/static/images/profiles/default_30.png",
            has_image=user_profile.has_profile_image,
        )
