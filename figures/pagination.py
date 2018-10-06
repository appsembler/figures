'''Paginatiors for Figures

'''

from rest_framework.pagination import LimitOffsetPagination

from figures.settings import DEFAULT_PAGINATION_LIMIT


class FiguresLimitOffsetPagination(LimitOffsetPagination):
    '''Custom Figures paginator to make the number of records returned consistent
    '''
    default_limit = DEFAULT_PAGINATION_LIMIT
