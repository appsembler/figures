
from rest_framework import serializers

###
### Summary serializers for listing
###

class CourseIndexSerializer(serializers.Serializer):
    '''
    Provides limited set of course overview infomration. The full set returned
    by the edx-platform built-in course api can be found in this class:

        lms.djangoapps.course_api.serializers.CourseSerializer
    '''

    id = serializers.CharField()
    name = serializers.CharField(source='display_name_with_default_escaped')
    org = serializers.CharField(source='display_org_with_default')
    number = serializers.CharField(source='display_number_with_default')
