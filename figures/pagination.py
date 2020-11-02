'''Paginatiors for Figures

'''

from __future__ import absolute_import
from rest_framework.pagination import LimitOffsetPagination


class FiguresLimitOffsetPagination(LimitOffsetPagination):
    '''Custom Figures paginator to make the number of records returned consistent
    '''
    default_limit = 20


class FiguresKiloPagination(LimitOffsetPagination):
    '''Custom Figures paginator to make the number of records returned consistent
    '''
    default_limit = 1000
