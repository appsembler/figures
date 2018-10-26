# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('figures', '0002_course_daily_metrics'),
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('error_type', models.CharField(default=b'UNS', max_length=3, choices=[(b'UNS', b'Unspecified data error'), (b'GRA', b'Grades data error'), (b'COU', b'Course data error'), (b'SIT', b'Site data error')])),
                ('error_data', jsonfield.fields.JSONField()),
                ('course_id', models.CharField(max_length=255, blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
