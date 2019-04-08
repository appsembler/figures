from figures.pagination import FiguresLimitOffsetPagination


class TestFiguresLimitOffsetPagination(object):
    '''

    '''
    def test_default_pagination_limit(self):
        assert FiguresLimitOffsetPagination.default_limit == 20
