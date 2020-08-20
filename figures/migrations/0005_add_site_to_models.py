# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models

# TODO Review on_delete behaviour
class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('figures', '0004_learner_course_grade_metrics'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sitedailymetrics',
            options={'ordering': ['-date_for', 'site']},
        ),
        migrations.AddField(
            model_name='coursedailymetrics',
            name='site',
            field=models.ForeignKey(default=1, to='sites.Site', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='learnercoursegrademetrics',
            name='site',
            field=models.ForeignKey(default=1, to='sites.Site', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='pipelineerror',
            name='site',
            field=models.ForeignKey(blank=True, to='sites.Site', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='sitedailymetrics',
            name='site',
            field=models.ForeignKey(default=1, to='sites.Site', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='sitedailymetrics',
            name='date_for',
            field=models.DateField(),
        ),
    ]
