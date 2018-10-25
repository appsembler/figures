'''

'''
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
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
from student.models import CourseEnrollment

from .filters import (
    CourseDailyMetricsFilter,
    CourseEnrollmentFilter,
    CourseOverviewFilter,
    SiteDailyMetricsFilter,
    UserFilterSet,
)
from .models import CourseDailyMetrics, SiteDailyMetrics
from .serializers import (
    CourseDailyMetricsSerializer,
    CourseDetailsSerializer,
    CourseEnrollmentSerializer,
    CourseIndexSerializer,
    GeneralCourseDataSerializer,

    LearnerDetailsSerializer,
    SiteDailyMetricsSerializer,
    UserIndexSerializer,
    GeneralUserDataSerializer
)
from figures import metrics
from figures.pagination import FiguresLimitOffsetPagination
from figures.permissions import IsStaffUser


UNAUTHORIZED_USER_REDIRECT_URL = '/'


#
# UI Template rendering views
#

@ensure_csrf_cookie
@login_required
@user_passes_test(lambda u: u.is_active and (u.is_staff or u.is_superuser),
                  login_url=UNAUTHORIZED_USER_REDIRECT_URL,
                  redirect_field_name=None)
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


#
# Mixins for API views
#

class CommonAuthMixin(object):
    '''Provides a common authorization base for the Figures API views

    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication, )
    permission_classes = (IsAuthenticated, IsStaffUser, )


#
# Views for data in edX platform
#


# @view_auth_classes(is_authenticated=True)
class CoursesIndexViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
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
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseIndexSerializer

    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseOverviewFilter

    def get_queryset(self):
        '''

        '''
        queryset = super(CoursesIndexViewSet, self).get_queryset()
        return queryset


class UserIndexViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''Provides a list of users with abbreviated details

    Uses figures.filters.UserFilter to select subsets of User objects
    '''
    model = get_user_model()
    queryset = get_user_model().objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = UserIndexSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        queryset = super(UserIndexViewSet, self).get_queryset()
        return queryset


class CourseEnrollmentViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    model = CourseEnrollment
    queryset = CourseEnrollment.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseEnrollmentSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseEnrollmentFilter

    def get_queryset(self):
        queryset = super(CourseEnrollmentViewSet, self).get_queryset()
        return queryset


#
# Views for Figures models
#

class CourseDailyMetricsViewSet(CommonAuthMixin, viewsets.ModelViewSet):

    model = CourseDailyMetrics
    queryset = CourseDailyMetrics.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseDailyMetricsFilter

    def get_queryset(self):
        queryset = super(CourseDailyMetricsViewSet, self).get_queryset()
        return queryset


class SiteDailyMetricsViewSet(CommonAuthMixin, viewsets.ModelViewSet):

    model = SiteDailyMetrics
    queryset = SiteDailyMetrics.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = SiteDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = SiteDailyMetricsFilter

    def get_queryset(self):
        queryset = super(SiteDailyMetricsViewSet, self).get_queryset()
        return queryset


#
# Views for the front end
#


class GeneralSiteMetricsView(CommonAuthMixin, APIView):
    '''
    Initial version assumes a single site.
    Multi-tenancy will add a Site foreign key to the SiteDailyMetrics model
    and list the most recent data for all sites (or filtered sites)
    '''

    pagination_class = FiguresLimitOffsetPagination

    @property
    def metrics_method(self):
        '''
            A bit of a hack until we refactor the metrics methods into classes.
            This lets us override this functionality, in particular to simplify
            testing
        '''
        return metrics.get_monthly_site_metrics

    def get(self, request, format=None):
        '''
        Does not yet support multi-tenancy
        '''

        date_for = request.query_params.get('date_for')

        data = self.metrics_method(date_for=date_for)

        if not data:
            data = {
                'error': 'no metrics data available',
            }
        return Response(data)


class GeneralCourseDataViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''

    '''
    model = CourseOverview
    queryset = CourseOverview.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = GeneralCourseDataSerializer

    def retrieve(self, request, *args, **kwargs):
        course_id_str = kwargs.get('pk', '')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        course_overview = get_object_or_404(CourseOverview, pk=course_key)
        return Response(GeneralCourseDataSerializer(course_overview).data)


class CourseDetailsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''

    '''
    model = CourseOverview
    queryset = CourseOverview.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseDetailsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseOverviewFilter

    def retrieve(self, request, *args, **kwargs):

        # NOTE: Duplicating code in GeneralCourseDataViewSet. Candidate to dry up
        course_id_str = kwargs.get('pk', '')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        course_overview = get_object_or_404(CourseOverview, pk=course_key)
        return Response(CourseDetailsSerializer(course_overview).data)


class GeneralUserDataViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''View class to serve general user data to the Figures UI

    See the serializer class, GeneralUserDataSerializer for the specific fields
    returned

    Can filter users for a specific course by providing the 'course_id' query
    parameter

    '''
    model = get_user_model()
    queryset = get_user_model().objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = GeneralUserDataSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        queryset = super(GeneralUserDataViewSet, self).get_queryset()
        return queryset


class LearnerDetailsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):

    queryset = get_user_model().objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = LearnerDetailsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        '''
        '''
        queryset = super(LearnerDetailsViewSet, self).get_queryset()
        return queryset
