'''Tests Figures PipeLineError model

'''

from __future__ import absolute_import
import datetime
import pytest

from figures.models import PipelineError


@pytest.mark.django_db
class TestPipelineError(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.error_data = dict(
            value1='value1',
            datetime_val=datetime.datetime(2018, 2, 2, 6, 30)
            )

    def test_error_data(self):
        obj = PipelineError(error_data=self.error_data)
        assert obj.error_data == self.error_data

    def test_create_unspecified(self):

        obj = PipelineError(error_data=self.error_data)
        assert obj.error_type == PipelineError.UNSPECIFIED_DATA

    @pytest.mark.parametrize('error_type,', [
        PipelineError.UNSPECIFIED_DATA,
        PipelineError.GRADES_DATA,
        PipelineError.COURSE_DATA,
        PipelineError.SITE_DATA,
    ])
    def test_create_with_error_type(self, error_type):
        obj = PipelineError(
            error_data=self.error_data,
            error_type=error_type,
            )
        assert obj.error_type == error_type

    def test_str(self):
        obj = PipelineError.objects.create(
            error_data=self.error_data,
            error_type=PipelineError.GRADES_DATA)
        assert str(obj) == '{}, {}, {}'.format(obj.id, obj.created, obj.error_type)
