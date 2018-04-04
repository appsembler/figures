from django.shortcuts import render

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.filters import DjangoFilterBackend

# Temp
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from .filters import CourseOverviewFilter

from .serializers import (
    CourseIndexSerializer,
)
# UI Template rendering views

# TODO: Do we have a need/want to make this a view class?

def edx_figures_home(request):

    # Placeholder context vars just to illustrate returning API hosts to the
    # client. This one uses a protocol relative url
    context = {
        'edx_figures_api_url': '//api.foo.com',
    }
    return render(request, 'edx_figures/index.html', context)


# We're going straight to the model so that we ensure we
# are getting the behavior we want.

#@view_auth_classes(is_authenticated=True)
class CoursesIndexView(ListAPIView):
    '''
    Provides a list of courses with abbreviated details

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
