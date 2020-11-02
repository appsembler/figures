# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('figures', '0006_remove_default_site_from_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedailymetrics',
            name='average_progress',
            field=models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2, validators=[django.core.validators.MaxValueValidator(1.0), django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
