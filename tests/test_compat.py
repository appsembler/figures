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
import types


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


# For the ficus and ginkgo tests, we need to first remove finding the hawthorn
# module


def test_course_grade_factory_with_ficus():
    hawthorn_key = 'lms.djangoapps.grades.course_grade_factory'
    namespaces = ['lms.djangoapps.grades.new',
                  'lms.djangoapps.grades.new.course_grade']
    modules = [types.ModuleType(ns) for ns in namespaces]
    modules[0].course_grade_factory = modules[1]
    setattr(modules[1], 'CourseGradeFactory', 'hi')
    with mock.patch.dict('sys.modules', {hawthorn_key: None}):
        with mock.patch.dict('sys.modules', {namespaces[0]: modules[0]}):
            with mock.patch.dict('sys.modules', {namespaces[1]: modules[1]}):
                import figures.compat
                reload(figures.compat)
                assert figures.compat.CourseGradeFactory == 'hi'


def test_course_grade_factory_with_ginkgo():
    hawthorn_key = 'lms.djangoapps.grades.course_grade_factory'
    namespaces = ['lms.djangoapps.grades.new',
                   'lms.djangoapps.grades.new.course_grade_factory']
    modules = [types.ModuleType(ns) for ns in namespaces]
    modules[0].course_grade_factory = modules[1]
    setattr(modules[1], 'CourseGradeFactory', 'hi')
    with mock.patch.dict('sys.modules', {hawthorn_key: None}):
        with mock.patch.dict('sys.modules', {namespaces[0]: modules[0]}):
            with mock.patch.dict('sys.modules', {namespaces[1]: modules[1]}):
                import figures.compat
                reload(figures.compat)
                assert figures.compat.CourseGradeFactory == 'hi'


def test_course_grade_factory_with_hawthorn():
    key = 'lms.djangoapps.grades.course_grade_factory'
    module = mock.Mock()
    setattr(module, 'CourseGradeFactory', 'hi')
    with mock.patch.dict('sys.modules', {key: module}):
        import figures.compat
        reload(figures.compat)
        assert hasattr(figures.compat, 'CourseGradeFactory')
        assert figures.compat.CourseGradeFactory == 'hi'


def test_generated_certificate_pre_hawthorn():
    hawthorn_key = 'lms.djangoapps.certificates.models'
    pre_haw_namespaces = ['certificates', 'certificates.models']
    modules = [types.ModuleType(ns) for ns in pre_haw_namespaces]
    modules[0].models = modules[1]
    setattr(modules[1], 'GeneratedCertificate', 'hi')
    with mock.patch.dict('sys.modules', {hawthorn_key: None}):
        with mock.patch.dict('sys.modules', {pre_haw_namespaces[0]: modules[0]}):
            with mock.patch.dict('sys.modules', {pre_haw_namespaces[1]: modules[1]}):
                import figures.compat
                reload(figures.compat)
                assert hasattr(figures.compat, 'GeneratedCertificate')
                assert figures.compat.GeneratedCertificate == 'hi'


def test_generated_certificate_hawthorn():
    hawthorn_key = 'lms.djangoapps.certificates.models'
    module = mock.Mock()
    setattr(module, 'GeneratedCertificate', 'hi')
    with mock.patch.dict('sys.modules', {hawthorn_key: module}):
        import figures.compat
        reload(figures.compat)
        assert hasattr(figures.compat, 'GeneratedCertificate')
        assert figures.compat.GeneratedCertificate == 'hi'


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
