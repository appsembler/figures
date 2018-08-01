
import pytest


from figures.pagination import FiguresLimitOffsetPagination
from figures.settings import DEFAULT_PAGINATION_LIMIT


class TestFiguresLimitOffsetPagination(object):
    '''

    '''
    def test_default_pagination_limit(self):
        assert DEFAULT_PAGINATION_LIMIT == 20
        assert FiguresLimitOffsetPagination.default_limit == DEFAULT_PAGINATION_LIMIT
