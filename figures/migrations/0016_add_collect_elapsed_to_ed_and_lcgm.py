# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('figures', '0015_add_enrollment_data_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollmentdata',
            name='collect_elapsed',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='learnercoursegrademetrics',
            name='collect_elapsed',
            field=models.FloatField(null=True),
        ),
    ]
