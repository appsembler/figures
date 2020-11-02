# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('figures', '0003_pipelineerror'),
    ]
    # TODO Review on_delete bahviour
    operations = [
        migrations.CreateModel(
            name='LearnerCourseGradeMetrics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('date_for', models.DateField()),
                ('course_id', models.CharField(max_length=255, blank=True)),
                ('points_possible', models.FloatField()),
                ('points_earned', models.FloatField()),
                ('sections_worked', models.IntegerField()),
                ('sections_possible', models.IntegerField()),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('date_for', 'user__username', 'course_id'),
            },
        ),
        migrations.AlterModelOptions(
            name='pipelineerror',
            options={'ordering': ['-created']},
        ),
        migrations.AlterUniqueTogether(
            name='learnercoursegrademetrics',
            unique_together=set([('user', 'course_id', 'date_for')]),
        ),
    ]
