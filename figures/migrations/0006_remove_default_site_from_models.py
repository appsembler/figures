# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('figures', '0005_add_site_to_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedailymetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='learnercoursegrademetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='sitedailymetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
        ),
    ]
