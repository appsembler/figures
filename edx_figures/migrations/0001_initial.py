# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('report_url', models.URLField(max_length=300, blank=True)),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('report_type', models.CharField(max_length=80, choices=[((b'LEARNER_DEMOGRAPHICS',), b'Learner Demographics Report'), (b'ENROLLMENT_GRADES', b'Enrollment and Grades Report')])),
                ('report_version', models.CharField(default=b'0.1.0', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='LearnerReportRowData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField()),
                ('learner_report', models.ForeignKey(related_name='learner_report', to='edx_figures.LearnerReport')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
