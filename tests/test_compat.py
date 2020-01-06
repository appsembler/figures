'''Tests Figures compat module

This test module makes no assumptions about the state of the mocks included in
pytest.ini

NOTE
====

Pytest monkeypatch does not support testing imports as it does not undo updating
entries in sys.modules. Therefore, we need to use patch context manager.

'''


# TODO:  copy test_compat.py and figures/compat.py off,
# wipe the branch, pull from develop and create new branch. Fastest


from mock import Mock, patch
import pytest
import six
from types import ModuleType


def patch_module(module_path, extra_properties=None):
    """
    Patch an entirely new module.

    This can be used as both decorator or a context (e.g. `with patch_module(...):`).

    :param module_path: lms.djangoapps.certificates.models
    :param extra_properties: {'SomeClass': Mock()}
    :return:
    """
    if not module_path:
        raise ValueError('module_path is required')

    path_parts = module_path.split('.')
    patch_specs = {}

    for i, part in enumerate(path_parts):
        sub_path = '.'.join(path_parts[:i+1])
        print('sub_path', sub_path)
        module = ModuleType(sub_path)
        patch_specs[sub_path] = module

        if i == (len(path_parts) - 1):  # Leaf module
            if extra_properties:
                for key, value in six.iteritems(extra_properties):
                    setattr(module, key, value)

    return patch.dict('sys.modules', patch_specs)


@patch('openedx.core.release.RELEASE_LINE', 'ginkgo')
def test_release_line_with_ginkgo():
    '''Make sure that ``figures.compat.RELEASE_LINE`` is 'ginkgo'
    '''
    with patch_module('certificates.models', {'GeneratedCertificate': Mock()}):  # Just to avoid an error
        import figures.compat
        reload(figures.compat)
        assert figures.compat.RELEASE_LINE == 'ginkgo'


# For the ginkgo tests, we need to first remove finding the hawthorn module

def test_course_grade_factory_with_ginkgo():
    hawthorn_key = 'lms.djangoapps.grades.course_grade_factory'
    with patch.dict('sys.modules', {hawthorn_key: None}):
        with patch_module('lms.djangoapps.grades.new.course_grade_factory', {'CourseGradeFactory': 'hi'}):
            import figures.compat
            reload(figures.compat)
            assert figures.compat.CourseGradeFactory == 'hi'


@patch('openedx.core.release.RELEASE_LINE', 'hawthorn')
def test_course_grade_factory_with_hawthorn():
    with patch_module('lms.djangoapps.certificates.models', {'GeneratedCertificate': Mock()}):  # Just to avoid an error
        with patch_module('lms.djangoapps.grades.course_grade_factory', {'CourseGradeFactory': 'hi'}):
            import figures.compat
            reload(figures.compat)
            assert hasattr(figures.compat, 'CourseGradeFactory')
            assert figures.compat.CourseGradeFactory == 'hi'


@patch('openedx.core.release.RELEASE_LINE', 'ginkgo')
def test_generated_certificate_pre_hawthorn():
    mock =  Mock()
    with patch_module('certificates.models', {'GeneratedCertificate': mock}):
        import figures.compat
        reload(figures.compat)
        assert hasattr(figures.compat, 'GeneratedCertificate')
        assert figures.compat.GeneratedCertificate is mock


@patch('openedx.core.release.RELEASE_LINE', 'hawthorn')
def test_generated_certificate_hawthorn():
    hawthorn_key = 'lms.djangoapps.certificates.models'
    with patch_module(hawthorn_key, {'GeneratedCertificate': 'hi'}):
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
