"""Figures views
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
import django.contrib.sites.shortcuts
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import NotFound
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

from figures.filters import (
    CourseDailyMetricsFilter,
    CourseEnrollmentFilter,
    CourseMauMetricsFilter,
    CourseOverviewFilter,
    SiteDailyMetricsFilter,
    SiteFilterSet,
    SiteMauMetricsFilter,
    UserFilterSet,
)
from figures.models import (
    CourseDailyMetrics,
    CourseMauMetrics,
    SiteDailyMetrics,
    SiteMauMetrics,
)
from figures.serializers import (
    CourseDailyMetricsSerializer,
    CourseDetailsSerializer,
    CourseEnrollmentSerializer,
    CourseIndexSerializer,
    CourseMauMetricsSerializer,
    CourseMauLiveMetricsSerializer,
    GeneralCourseDataSerializer,
    LearnerDetailsSerializer,
    SiteDailyMetricsSerializer,
    SiteMauMetricsSerializer,
    SiteMauLiveMetricsSerializer,
    SiteSerializer,
    UserIndexSerializer,
    GeneralUserDataSerializer,
)
from figures import metrics
from figures.pagination import (
    FiguresLimitOffsetPagination,
    FiguresKiloPagination,
)
import figures.permissions
import figures.helpers
import figures.sites
from figures.mau import (
    retrieve_live_course_mau_data,
    retrieve_live_site_mau_data,
)


UNAUTHORIZED_USER_REDIRECT_URL = '/'


#
# UI Template rendering views
#

@ensure_csrf_cookie
@login_required
@user_passes_test(lambda u: u.is_active,
                  login_url=UNAUTHORIZED_USER_REDIRECT_URL,
                  redirect_field_name=None)
def figures_home(request):
    '''Renders the JavaScript SPA dashboard


    TODO: Should we make this a view class?

    '''
    # We probably want to roll this into a decorator
    if not figures.permissions.is_site_admin_user(request):
        return HttpResponseRedirect('/')

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
    TODO: Consider moving this to figures.permissions
    '''
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
        figures.permissions.IsSiteAdminUser,
    )


class StaffUserOnDefaultSiteAuthMixin(object):
    '''Provides a common authorization base for the Figures API views
    TODO: Consider moving this to figures.permissions
    '''
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
        figures.permissions.IsStaffUserOnDefaultSite,
    )

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
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseIndexSerializer

    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseOverviewFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_courses_for_site(site)
        return queryset


class UserIndexViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''Provides a list of users with abbreviated details

    Uses figures.filters.UserFilter to select subsets of User objects
    '''
    model = get_user_model()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = UserIndexSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_users_for_site(site)
        return queryset


class CourseEnrollmentViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    model = CourseEnrollment
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseEnrollmentSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseEnrollmentFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_course_enrollments_for_site(site)
        return queryset

#
# Views for Figures models
#


class CourseDailyMetricsViewSet(CommonAuthMixin, viewsets.ModelViewSet):

    model = CourseDailyMetrics
    # queryset = CourseDailyMetrics.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = CourseDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseDailyMetricsFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = CourseDailyMetrics.objects.filter(site=site)
        return queryset


class SiteDailyMetricsViewSet(CommonAuthMixin, viewsets.ModelViewSet):

    model = SiteDailyMetrics
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = SiteDailyMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = SiteDailyMetricsFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = SiteDailyMetrics.objects.filter(site=site)
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
        site = django.contrib.sites.shortcuts.get_current_site(request)
        date_for = request.query_params.get('date_for')
        data = self.metrics_method(site=site, date_for=date_for)

        if not data:
            data = {
                'error': 'no metrics data available',
            }
        return Response(data)


class GeneralCourseDataViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''

    '''
    model = CourseOverview

    # The "kilo paginator"  is a tempoarary hack to return all course to not
    # have to change the front end until Figures "Level 2"
    pagination_class = FiguresKiloPagination
    serializer_class = GeneralCourseDataSerializer

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_courses_for_site(site)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        course_id_str = kwargs.get('pk', '')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        site = django.contrib.sites.shortcuts.get_current_site(request)
        if figures.helpers.is_multisite():
            if site != figures.sites.get_site_for_course(course_key):
                # Raising NotFound instead of PermissionDenied
                raise NotFound()
        course_overview = get_object_or_404(CourseOverview, pk=course_key)
        return Response(GeneralCourseDataSerializer(course_overview).data)


class CourseDetailsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''

    '''
    model = CourseOverview

    # The "kilo paginator"  is a tempoarary hack to return all course to not
    # have to change the front end until Figures "Level 2"
    pagination_class = FiguresKiloPagination
    serializer_class = CourseDetailsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseOverviewFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_courses_for_site(site)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        # NOTE: Duplicating code in GeneralCourseDataViewSet. Candidate to dry up
        # Make it a decorator
        course_id_str = kwargs.get('pk', '')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        site = django.contrib.sites.shortcuts.get_current_site(request)
        if figures.helpers.is_multisite():
            if site != figures.sites.get_site_for_course(course_key):
                # Raising NotFound instead of PermissionDenied
                raise NotFound()
        course_overview = get_object_or_404(CourseOverview, pk=course_key)
        return Response(CourseDetailsSerializer(course_overview).data)


class GeneralUserDataViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    '''View class to serve general user data to the Figures UI

    See the serializer class, GeneralUserDataSerializer for the specific fields
    returned

    Can filter users for a specific course by providing the 'course_id' query
    parameter

    TODO: Make this class and any other User model based viewsets inherit a
    base. The only difference between them is the serializer
    '''
    model = get_user_model()
    pagination_class = FiguresKiloPagination
    serializer_class = GeneralUserDataSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_users_for_site(site)
        return queryset


class LearnerDetailsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    model = get_user_model()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = LearnerDetailsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilterSet

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = figures.sites.get_users_for_site(site)
        return queryset

    def get_serializer_context(self):
        context = super(LearnerDetailsViewSet, self).get_serializer_context()
        context['site'] = django.contrib.sites.shortcuts.get_current_site(self.request)
        return context


class CourseMauLiveMetricsViewSet(CommonAuthMixin, viewsets.GenericViewSet):
    serializer_class = CourseMauLiveMetricsSerializer

    def get_queryset(self):
        """
        Stub method because ViewSet requires one, even though we are not
        retrieving querysets directly (we use the query in figures.sites)
        """
        pass

    def retrieve(self, request, *args, **kwargs):
        course_id_str = kwargs.get('pk', '')
        course_key = CourseKey.from_string(course_id_str.replace(' ', '+'))
        site = django.contrib.sites.shortcuts.get_current_site(self.request)

        if figures.helpers.is_multisite():
            if site != figures.sites.get_site_for_course(course_key):
                # Raising NotFound instead of PermissionDenied
                raise NotFound()
        data = retrieve_live_course_mau_data(site, course_key)
        serializer = self.serializer_class(data)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        course_overviews = figures.sites.get_courses_for_site(site)
        data = []
        for co in course_overviews:
            data.append(retrieve_live_course_mau_data(site, co.id))
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)


class SiteMauLiveMetricsViewSet(CommonAuthMixin, viewsets.GenericViewSet):
    """
    Retrieve live MAU site metrics for the site called

    TODO: Potential future improvement is to display single site if the
    caller is a site admin for the given site and for all sites (paginated?)
    if the caller is a host (provider) level user
    """
    serializer_class = SiteMauLiveMetricsSerializer

    def get_queryset(self):
        """
        Stub method because ViewSet requires one, even though we are not
        retrieving querysets directly (we use the query in figures.sites)
        """
        pass

    def list(self, request, *args, **kwargs):
        """
        We use list instead of retrieve because retrieve requires a resource
        identifier, like a PK
        """
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        data = retrieve_live_site_mau_data(site)
        serializer = self.serializer_class(data)
        return Response(serializer.data)


class CourseMauMetricsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    model = CourseMauMetrics
    serializer_class = CourseMauMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = CourseMauMetricsFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = CourseMauMetrics.objects.filter(site=site)
        return queryset


class SiteMauMetricsViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):

    model = SiteMauMetrics
    serializer_class = SiteMauMetricsSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = SiteMauMetricsFilter

    def get_queryset(self):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        queryset = SiteMauMetrics.objects.filter(site=site)
        return queryset


class SiteViewSet(StaffUserOnDefaultSiteAuthMixin, viewsets.ReadOnlyModelViewSet):
    """Provides API access to the django.contrib.sites.models.Site model

    Access is restricted to global (Django instance) staff
    """
    model = Site
    queryset = Site.objects.all()
    pagination_class = FiguresLimitOffsetPagination
    serializer_class = SiteSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = SiteFilterSet
