'''
Defines models used in edx-figures

The ``LearnerReport`` and ``LearnerReportArchive`` models collect data
retrieved from the LMS in report generation. This serves the following purposes:

1. Ability to regenerate the report output for a given time
2. Ability to analyze timeseries data

'''

from datetime import timedelta

from django.conf import settings
from django.db import models

from jsonfield import JSONField


class LearnerReport(models.Model):
    '''
    This model serves as the top level record that collects data used in the
    row data for a report

    Model fields:

      created:     This is the timestamp when the report was created
      report_url:  This is the URL for the generated report file. Typically,
                   this would be a cloud provider bucket, like Amazon S3
      duration:    This is the amount of time it took to generate the report
      report_type: This identifies which kind of report has been generated.
                   Currently there are two kinds of reports:
                   ``LEARNER_DEMOGRAPHICS``
                   ``ENROLLMENT_GRADES``
      report_version:  This is an aide for handling backward compatibility
    '''


    REPORT_LEARNER_DEMOGRAPHICS = 'LEARNER_DEMOGRAPHICS',
    REPORT_ENROLLMENT_GRADES = 'ENROLLMENT_GRADES'

    REPORT_CHOICES = (
        (REPORT_LEARNER_DEMOGRAPHICS, "Learner Demographics Report"),
        (REPORT_ENROLLMENT_GRADES, "Enrollment and Grades Report"),
        )
    created = models.DateTimeField(auto_now_add=True)
    report_url = models.URLField(max_length=300, blank=True)
    duration = models.DurationField(default=timedelta()) # time it took to generate the report
    report_type = models.CharField(max_length=80, choices=REPORT_CHOICES)
    report_version = models.CharField(max_length=30, default='0.1.0')

    def __str__(self):
        return "{} {} {} {}".format(
            self.id, self.report_version, self.created, self.report_url
        )

class LearnerReportRowData(models.Model):
    '''
    Contains row level report data in a JSON "blob"

    Model fields:

      json: This contains a JSON serialized collection of key/value pairs. Each
            key/value pair represents a column in the generated report
      learner_report: Foreign key to the parent record
      user: One to One foreign key to the user (learner) from which these data
      have been produced


    NOTES:

      We currently don't indicate if data from a custom data model was used for
      a record. Custom data would come from a customer plugin app that contains
      a model defining custom registration fields
    '''

    json = JSONField()
    # Question: Do we need/desire a default sort order/sequence number for the
    # data for a given report?
    # sequence = models.IntegerField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    learner_report = models.ForeignKey(
        LearnerReport,
        related_name='learner_report',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    class Meta:
        # How to order based on value in parent?
        #ordering = ('')
        pass