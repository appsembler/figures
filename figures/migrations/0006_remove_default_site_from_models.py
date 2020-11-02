# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('figures', '0005_add_site_to_models'),
    ]
    #TODO Review on_delete behaviour
    operations = [
        migrations.AlterField(
            model_name='coursedailymetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='learnercoursegrademetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='sitedailymetrics',
            name='site',
            field=models.ForeignKey(to='sites.Site', on_delete=models.CASCADE),
        ),
    ]
