from __future__ import absolute_import
from figures.pagination import (
    FiguresLimitOffsetPagination,
    FiguresKiloPagination,
)


class TestFiguresLimitOffsetPagination(object):
    def test_default_pagination_limit(self):
        assert FiguresLimitOffsetPagination.default_limit == 20


class TestFigureKiloPagination(object):
    def test_default_pagination_limit(self):
        assert FiguresKiloPagination.default_limit == 1000
