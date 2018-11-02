'''Tests Figures compat module

This test module makes no assumptions about the state of the mocks included in
pytest.ini

NOTE
====

Pytest monkeypatch does not support testing imports as it does not undo updating
entries in sys.modules. Therefore, we need to use mock.patch context manager.

'''


# TODO:  copy test_compat.py and figures/compat.py off,
# wipe the branch, pull from develop and create new branch. Fastest


import mock
import pytest


def test_release_line_with_ficus():
    '''Make sure that ``figures.compat`` returns ``CourseGradeFactory`` from the
    Ficus module ``lms.djangoapps.grades.new.course_grade``
    '''

    with mock.patch.dict('sys.modules', {'openedx.core.release': None}):
        import figures.compat
        reload(figures.compat)
        assert not figures.compat.RELEASE_LINE


def test_release_line_with_ginkgo():
    '''Make sure that ``figures.compat.RELEASE_LINE`` is 'ginkgo'
    '''
    release_module = mock.MagicMock()
    setattr(release_module, 'RELEASE_LINE', 'ginkgo')

    with mock.patch.dict('sys.modules', {'openedx.core.release': release_module}):
        import figures.compat
        reload(figures.compat)
        assert figures.compat.RELEASE_LINE == 'ginkgo'


def test_course_grade_factory_with_ficus():
    '''Make sure that ``figures.compat`` returns ``CourseGradeFactory`` from the
    Ginkgo module, ``lms.djangoapps.grades.new.course_grade_factory``
    '''
    ficus_key = 'lms.djangoapps.grades.new.course_grade'
    ginkgo_key = 'lms.djangoapps.grades.new.course_grade_factory'
    with mock.patch.dict('sys.modules', {ginkgo_key: None}):
        module = mock.Mock()
        setattr(module, 'CourseGradeFactory', 'hi')
        with mock.patch.dict('sys.modules', {ficus_key: module}):
            import figures.compat
            reload(figures.compat)
            assert hasattr(figures.compat, 'CourseGradeFactory')
            assert figures.compat.CourseGradeFactory == 'hi'


def test_course_grade_factory_with_ginkgo():
    module = mock.Mock()
    setattr(module, 'CourseGradeFactory', 'hi')
    key = 'lms.djangoapps.grades.new.course_grade_factory'

    with mock.patch.dict('sys.modules', {key: module}):
        import figures.compat
        reload(figures.compat)
        assert hasattr(figures.compat, 'CourseGradeFactory')
        assert figures.compat.CourseGradeFactory == 'hi'


@pytest.mark.parametrize('chapter_grades, expected', [
        ({'some_key': ['a', 'b']}, [['a', 'b']]),
        (['a', 'b'], ['a', 'b']),
    ])
def test_chapter_grade_values(chapter_grades, expected):
    import figures.compat
    reload(figures.compat)
    val = figures.compat.chapter_grade_values(chapter_grades)
    assert val == expected


def test_chapter_grade_values_invalid():
    import figures.compat
    reload(figures.compat)
    with pytest.raises(TypeError):
        figures.compat.chapter_grade_values('hello world')
