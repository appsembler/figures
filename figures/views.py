'''

'''
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render

from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from opaque_keys.edx.keys import CourseKey

# Directly including edx-platform objects for early development
# Follow-on, we'll likely consolidate edx-platform model imports to an adapter
from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview,
)
from student.models import CourseEnrollment, UserProfile

from .filters import (
    CourseDailyMetricsFilter,
    CourseEnrollmentFilter,
    CourseOverviewFilter,
    GeneralUserDataFilter,
    SiteDailyMetricsFilter,
    UserFilter,
)
from .models import CourseDailyMetrics, SiteDailyMetrics
from .serializers import (
    CourseDailyMetricsSerializer,
    CourseEnrollmentSerializer,
    CourseIndexSerializer,
    GeneralCourseDataSerializer,
    GeneralSiteMetricsSerializer,
    SiteDailyMetricsSerializer,
    UserIndexSerializer,
    GeneralUserDataSerializer
)
from figures import metrics

##
## UI Template rendering views
##

def figures_home(request):
    '''Renders the JavaScript SPA dashboard


    TODO: Should we make this a view class?

    '''

    # Placeholder context vars just to illustrate returning API hosts to the
    # client. This one uses a protocol relative url
    context = {
        'figures_api_url': '//api.example.com',
    }
    return render(request, 'figures/index.html', context)


##
## Views for data in edX platform
##

# We're going straight to the model so that we ensure we
# are getting the behavior we want.

#@view_auth_classes(is_authenticated=True)
class CoursesIndexView(ListAPIView):
    '''Provides a list of courses with abbreviated details

    Uses figures.filters.CourseOverviewFilter to select subsets of
    CourseOverview objects

    We want to be able to filter on
    - org: exact and search
    - name: exact and search
    - description search
    - enrollment start
    - enrollment end
    - start
    - end

    '''
    model = CourseOverview
    queryset = CourseOverview.objects.all()
    pagination_class = None
    serializer_class = CourseIndexSerializer

    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseOverviewFilter

    def get_queryset(self):
        '''

        '''
        queryset = super(CoursesIndexView, self).get_queryset()

        return queryset


# TODO: Add authorization
class UserIndexView(ListAPIView):
    '''Provides a list of users with abbreviated details

    Uses figures.filters.UserFilter to select subsets of User objects
    '''

    model = get_user_model()
    queryset = get_user_model().objects.all()
    pagination_class = None
    serializer_class = UserIndexSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilter

    def get_queryset(self):
        queryset = super(UserIndexView, self).get_queryset()

        return queryset

# TODO: Change to ReadOnlyModelViewSet
class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    model = CourseEnrollment
    queryset = CourseEnrollment.objects.all()
    pagination_class = None
    serializer_class = CourseEnrollmentSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseEnrollmentFilter

    def get_queryset(self):
        queryset = super(CourseEnrollmentViewSet, self).get_queryset()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

##
## Views for Figures models
##

class CourseDailyMetricsViewSet(viewsets.ModelViewSet):

    model = CourseDailyMetrics
    queryset = CourseDailyMetrics.objects.all()
    pagination_class = None
    serializer_class = CourseDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseDailyMetricsFilter

    def get_queryset(self):
        queryset = super(CourseDailyMetricsViewSet, self).get_queryset()
        return queryset


#class SiteDailyMetricsViewSet(CommonAuthMixin, viewsets.ModelViewSet):
class SiteDailyMetricsViewSet(viewsets.ModelViewSet):

    model = SiteDailyMetrics
    queryset = SiteDailyMetrics.objects.all()
    pagination_class = None
    serializer_class = SiteDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = SiteDailyMetricsFilter

    def get_queryset(self):
        queryset = super(SiteDailyMetricsViewSet, self).get_queryset()
        return queryset


##
## Views for the front end
##

class GeneralSiteMetricsView(APIView):
    '''
    Initial version assumes a single site.
    Multi-tenancy will add a Site foreign key to the SiteDailyMetrics model
    and list the most recent data for all sites (or filtered sites)
    '''

    # queryset = SiteDailyMetrics.objects.all()
    # pagination_class = None
    # serializer_class = GeneralSiteMetricsSerializer
    #TODO add filters

    def get(self, request, format=None):
        '''
        Does not yet support multi-tenancy
        '''

        date_for = request.query_params.get('date_for')
        data = metrics.get_monthly_site_metrics(date_for=date_for)

        if not data:
            data = {
                'error': 'no metrics data available',
            }
        return Response(data)


    # def list(self, request):

    #     #queryset = self.filter_queryset(self.get_queryset())
    #     queryset = 
    #     serializer = self.get_serializer(queryset, many=True)

    #     return Response(serializer.data)

    # def retrieve(self, request, thread_id=None):
    #     """
    #     Implements the GET method for thread ID
    #     """
    #     requested_fields = request.GET.get('requested_fields')
    #     return Response(get_thread(request, thread_id, requested_fields))

    # def retrieve(self, request, site_id=None):
    #     """
    #     Implements the GET method for thread ID
    #     """
    #     requested_fields = request.GET.get('requested_fields')
    #     return Response(get_thread(request, thread_id, requested_fields))


class GeneralCourseDataViewSet(viewsets.ModelViewSet):
    '''

    '''
    model = CourseOverview
    queryset = CourseOverview.objects.all()
    pagination_class = None
    serializer_class = GeneralCourseDataSerializer

    def retrieve(self, request, *args, **kwargs):
        course_id_str = kwargs.get('pk','')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        course_overview = get_object_or_404(CourseOverview, pk=course_key)
        return Response(GeneralCourseDataSerializer(course_overview).data)


class GeneralUserDataViewSet(viewsets.ReadOnlyModelViewSet):
    '''View class to serve general user data to the Figures UI

    See the serializer class, GeneralUserDataSerializer for the specific fields
    returned

    Can filter users for a specific course by providing the 'course_id' query
    parameter

    '''
    model = get_user_model()
    queryset =  get_user_model().objects.all()
    pagination_class = None
    serializer_class = GeneralUserDataSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = GeneralUserDataFilter

    def get_queryset(self):
        queryset = super(GeneralUserDataViewSet, self).get_queryset()
        return queryset
