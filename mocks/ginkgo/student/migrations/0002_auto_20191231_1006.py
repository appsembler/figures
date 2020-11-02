# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='allow_certificate',
            field=models.BooleanField(default=1),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(max_length=3000, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='goals',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mailing_address',
            field=models.TextField(null=True, blank=True),
        ),
    ]
