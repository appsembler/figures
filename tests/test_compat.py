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


from __future__ import absolute_import
from __future__ import print_function
from types import ModuleType
import six
import pytest

try:
    from importlib import reload
except ImportError:
    pass

from mock import patch


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
        print(('sub_path', sub_path))
        module = ModuleType(sub_path)
        patch_specs[sub_path] = module

        if i == (len(path_parts) - 1):  # Leaf module
            if extra_properties:
                for key, value in six.iteritems(extra_properties):
                    setattr(module, key, value)

    return patch.dict('sys.modules', patch_specs)


# TODO: Test with no release line


@patch('openedx.core.release.RELEASE_LINE', 'ginkgo')
def test_compat_module_with_ginkgo():
    """Test Ginkgo compat path works

    Yes, we have a number of assertions here. We are testing the state of
    `figures.compat` when we expect Figures to run in Ginkgo. Running in one
    test also saves execution time as we need to ste up the whole module to
    import as Ginkgo even if we are only testing one object in the module
    """
    with patch_module('lms.djangoapps.grades.new.course_grade_factory',
                      {'CourseGradeFactory': 'cgf'}):
        with patch_module('certificates.models', {'GeneratedCertificate': 'gc'}):
            with patch_module('courseware.models', {'StudentModule': 'sm'}):
                with patch_module('courseware.courses', {'get_course_by_id': 'gcbid'}):
                    with patch_module('openedx.core.djangoapps.xmodule_django.models',
                                      {'CourseKeyField': 'ckf'}):
                        import figures.compat
                        reload(figures.compat)
                        assert figures.compat.RELEASE_LINE == 'ginkgo'
                        assert hasattr(figures.compat, 'CourseGradeFactory')
                        assert figures.compat.CourseGradeFactory == 'cgf'
                        assert hasattr(figures.compat, 'GeneratedCertificate')
                        assert figures.compat.GeneratedCertificate == 'gc'
                        assert hasattr(figures.compat, 'StudentModule')
                        assert figures.compat.StudentModule == 'sm'
                        assert hasattr(figures.compat, 'get_course_by_id')
                        assert figures.compat.get_course_by_id == 'gcbid'
                        assert hasattr(figures.compat, 'CourseKeyField')
                        assert figures.compat.CourseKeyField == 'ckf'


@patch('openedx.core.release.RELEASE_LINE', 'hawthorn')
def test_release_line_with_hawthorn():
    """Test Hawthorn compat path works

    Yes, we have a number of assertions here. We are testing the state of
    `figures.compat` when we expect Figures to run in Ginkgo. Running in one
    test also saves execution time as we need to ste up the whole module to
    import as Ginkgo even if we are only testing one object in the module
    """
    with patch_module('lms.djangoapps.grades.course_grade_factory',
                      {'CourseGradeFactory': 'cgf'}):
        with patch_module('lms.djangoapps.certificates.models',
                          {'GeneratedCertificate': 'gc'}):
            with patch_module('courseware.models', {'StudentModule': 'sm'}):
                with patch_module('courseware.courses',
                                  {'get_course_by_id': 'gcbid'}):
                    with patch_module('opaque_keys.edx.django.models',
                                      {'CourseKeyField': 'ckf'}):
                        import figures.compat
                        reload(figures.compat)
                        assert figures.compat.RELEASE_LINE == 'hawthorn'
                        assert hasattr(figures.compat, 'CourseGradeFactory')
                        assert figures.compat.CourseGradeFactory == 'cgf'
                        assert hasattr(figures.compat, 'GeneratedCertificate')
                        assert figures.compat.GeneratedCertificate == 'gc'
                        assert hasattr(figures.compat, 'StudentModule')
                        assert figures.compat.StudentModule == 'sm'
                        assert hasattr(figures.compat, 'get_course_by_id')
                        assert figures.compat.get_course_by_id == 'gcbid'
                        assert hasattr(figures.compat, 'CourseKeyField')
                        assert figures.compat.CourseKeyField == 'ckf'


@patch('openedx.core.release.RELEASE_LINE', 'juniper')
def test_release_line_with_juniper():
    """Test Hawthorn compat path works

    Yes, we have a number of assertions here. We are testing the state of
    `figures.compat` when we expect Figures to run in Ginkgo. Running in one
    test also saves execution time as we need to ste up the whole module to
    import as Ginkgo even if we are only testing one object in the module
    """
    with patch_module('lms.djangoapps.grades.course_grade_factory',
                      {'CourseGradeFactory': 'cgf'}):
        with patch_module('lms.djangoapps.certificates.models',
                          {'GeneratedCertificate': 'gc'}):
            with patch_module('lms.djangoapps.courseware.models',
                              {'StudentModule': 'sm'}):
                with patch_module('lms.djangoapps.courseware.courses',
                                  {'get_course_by_id': 'gcbid'}):
                    with patch_module('opaque_keys.edx.django.models',
                                      {'CourseKeyField': 'ckf'}):
                        import figures.compat
                        reload(figures.compat)
                        assert figures.compat.RELEASE_LINE == 'juniper'
                        assert hasattr(figures.compat, 'CourseGradeFactory')
                        assert figures.compat.CourseGradeFactory == 'cgf'
                        assert hasattr(figures.compat, 'GeneratedCertificate')
                        assert figures.compat.GeneratedCertificate == 'gc'
                        assert hasattr(figures.compat, 'StudentModule')
                        assert figures.compat.StudentModule == 'sm'
                        assert hasattr(figures.compat, 'get_course_by_id')
                        assert figures.compat.get_course_by_id == 'gcbid'
                        assert hasattr(figures.compat, 'CourseKeyField')
                        assert figures.compat.CourseKeyField == 'ckf'


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
