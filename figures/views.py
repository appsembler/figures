"""Figures views
"""

from datetime import datetime
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
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import (
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter
)
from rest_framework.response import Response
from rest_framework.views import APIView

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

# Directly including edx-platform objects for early development
# Follow-on, we'll likely consolidate edx-platform model imports to an adapter
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # noqa pylint: disable=import-error
from student.models import CourseEnrollment  # pylint: disable=import-error

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
    get_course_history_metric,
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
    """Viewset intended for Figures Web UI

    DEPRECATED. This view is deprecated

    TODO: Determine when we remove this class

    Initial version assumes a single site.
    Multi-tenancy will add a Site foreign key to the SiteDailyMetrics model
    and list the most recent data for all sites (or filtered sites)
    """

    pagination_class = FiguresLimitOffsetPagination

    @property
    def metrics_method(self):
        '''
            A bit of a hack until we refactor the metrics methods into classes.
            This lets us override this functionality, in particular to simplify
            testing
        '''
        return metrics.get_monthly_site_metrics

    def get(self, request, format=None):  # pylint: disable=redefined-builtin
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
    """Viewset intended for Figures Web UI
    """
    model = CourseOverview

    # The "kilo paginator"  is a tempoarary hack to return all course to not
    # have to change the front end until Figures "Level 2"
    pagination_class = FiguresKiloPagination
    serializer_class = GeneralCourseDataSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_class = CourseOverviewFilter
    search_fields = ['display_name', 'id']
    ordering_fields = ['display_name', 'self_paced', 'date_joined']

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
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_class = UserFilterSet
    search_fields = ['username', 'email', 'profile__name']
    ordering_fields = ['username', 'email', 'profile__name', 'is_active', 'date_joined']

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


class CourseMonthlyMetricsViewSet(CommonAuthMixin, viewsets.ViewSet):
    """

    """

    # TODO: Make 'months_back' be a query parameter.
    # We will also need to either set a limit or paginate history results
    months_back = 6

    def site_course_helper(self, pk):
        """Hep

        Improvements:
        * make this a decorator
        * Test this with both course id strings and CourseKey objects
        """
        course_id = pk.replace(' ', '+')
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            raise NotFound()

        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        if figures.helpers.is_multisite():
            if site != figures.sites.get_site_for_course(course_id):
                raise NotFound()
        else:
            get_object_or_404(CourseOverview,
                              pk=course_key)
        return site, course_id

    def historic_data(self, site, course_id, func, **_kwargs):
        date_for = _kwargs.get('date_for', datetime.utcnow().date())
        months_back = _kwargs.get('months_back', self.months_back)
        return get_course_history_metric(
            site=site,
            course_id=course_id,
            func=func,
            date_for=date_for,
            months_back=months_back
        )

    def list(self, request):
        """
        Returns site metrics data for current month

        TODO: NEXT Add query params to get data from previous months
        TODO: Add paginagation
        """
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        course_keys = figures.sites.get_course_keys_for_site(site)
        date_for = datetime.utcnow().date()
        month_for = '{}/{}'.format(date_for.month, date_for.year)
        data = []
        for course_key in course_keys:
            data.append(metrics.get_month_course_metrics(site=site,
                                                         course_id=str(course_key),
                                                         month_for=month_for))
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """
        TODO: Make sure we have a test to handle invalid or empty course id
        """
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))

        date_for = datetime.utcnow().date()
        month_for = '{}/{}'.format(date_for.month, date_for.year)
        data = metrics.get_month_course_metrics(site=site,
                                                course_id=course_id,
                                                month_for=month_for)
        return Response(data)

    @detail_route()
    def active_users(self, request, **kwargs):
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))
        date_for = datetime.utcnow().date()
        months_back = 6
        active_users = metrics.get_course_mau_history_metrics(
            site=site,
            course_id=course_id,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(active_users=active_users)
        return Response(data)

    @detail_route()
    def course_enrollments(self, request, *args, **kwargs):
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))
        data = dict(course_enrollments=self.historic_data(
            request=request,
            site=site,
            course_id=course_id,
            func=metrics.get_course_enrolled_users_for_time_period))
        return Response(data)

    @detail_route()
    def num_learners_completed(self, request, *args, **kwargs):
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))
        data = dict(num_learners_completed=self.historic_data(
            request=request,
            site=site,
            course_id=course_id,
            func=metrics.get_course_num_learners_completed_for_time_period))
        return Response(data)

    @detail_route()
    def avg_days_to_complete(self, request, *args, **kwargs):
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))
        data = dict(avg_days_to_complete=self.historic_data(
            request=request,
            site=site,
            course_id=course_id,
            func=metrics.get_course_average_days_to_complete_for_time_period))
        return Response(data)

    @detail_route()
    def avg_progress(self, request, *args, **kwargs):
        site, course_id = self.site_course_helper(kwargs.get('pk', ''))
        data = dict(avg_progress=self.historic_data(
            request=request,
            site=site,
            course_id=course_id,
            func=metrics.get_course_average_progress_for_time_period))
        return Response(data)


class SiteMonthlyMetricsViewSet(CommonAuthMixin, viewsets.ViewSet):
    """Serves sitewide metrics

    TODO:
    * Make months_back be a query param.
    * Create a decorator to do the duplicate work in these methods
    * Improve test coverage
    * Create viewsets for `SiteMetricsViewSet`, `UserMetricsViewSet`
    #   `CourseMetricsViewSet` for retrieving live data for each context

    ## Dev note
    Does it benefit to make serializers for these calls?
    Do we want to create a SiteMonthlyMetrics model?
    If we do, then we can also use django-filter on the model
    Tradeoff: Additional storage cost to reduced request time
    Perhaps we make this a server setting
    """
    def list(self, request):
        """
        Returns site metrics data for current month
        """

        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        data = metrics.get_current_month_site_metrics(site)
        return Response(data)

    @list_route()
    def registered_users(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        date_for = datetime.utcnow().date()
        months_back = 6

        registered_users = metrics.get_monthly_history_metric(
            func=metrics.get_total_site_users_for_time_period,
            site=site,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(registered_users=registered_users)
        return Response(data)

    @list_route()
    def new_users(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        date_for = datetime.utcnow().date()
        months_back = 6

        new_users = metrics.get_monthly_history_metric(
            func=metrics.get_total_site_users_joined_for_time_period,
            site=site,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(new_users=new_users)
        return Response(data)

    @list_route()
    def course_completions(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        date_for = datetime.utcnow().date()
        months_back = 6

        course_completions = metrics.get_monthly_history_metric(
            func=metrics.get_total_site_users_for_time_period,
            site=site,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(course_completions=course_completions)
        return Response(data)

    @list_route()
    def course_enrollments(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        date_for = datetime.utcnow().date()
        months_back = 6

        course_enrollments = metrics.get_monthly_history_metric(
            func=metrics.get_total_enrollments_for_time_period,
            site=site,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(course_enrollments=course_enrollments)
        return Response(data)

    @list_route()
    def site_courses(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        date_for = datetime.utcnow().date()
        months_back = 6

        site_courses = metrics.get_monthly_history_metric(
            func=metrics.get_total_site_courses_for_time_period,
            site=site,
            date_for=date_for,
            months_back=months_back,
        )
        data = dict(site_courses=site_courses)
        return Response(data)

    @list_route()
    def active_users(self, request):
        site = django.contrib.sites.shortcuts.get_current_site(self.request)
        months_back = 6
        active_users = metrics.get_site_mau_history_metrics(site=site,
                                                            months_back=months_back)
        return Response(dict(active_users=active_users))


#
# MAU metrics views
#


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
