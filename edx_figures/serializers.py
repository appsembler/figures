'''Serializers used in edX Figures

'''

from rest_framework import serializers

###
### Summary serializers for listing
###

class CourseIndexSerializer(serializers.Serializer):
    '''Provides a limited set of course overview information

    The full set returned by the edx-platform built-in course api can be found
    in this class:

        lms.djangoapps.course_api.serializers.CourseSerializer
    '''

    id = serializers.CharField()
    name = serializers.CharField(source='display_name_with_default_escaped')
    org = serializers.CharField(source='display_org_with_default')
    number = serializers.CharField(source='display_number_with_default')


class UserIndexSerializer(serializers.Serializer):
    '''Provides a limited set of user information for summary display
    '''
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    fullname = serializers.CharField(source='profile.name', default=None,
        read_only=True)
