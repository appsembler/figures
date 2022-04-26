# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    if DJANGO_VERSION[0:2] == (1,8):
        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
            ('sites', '0001_initial'),
            ('figures', '0016_add_collect_elapsed_to_ed_and_lcgm'),
        ]
    else:  # Assuming 1.11+
        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
            ('sites', '0002_alter_domain_unique'),
            ('figures', '0016_add_collect_elapsed_to_ed_and_lcgm'),
        ]

    operations = [
        migrations.CreateModel(
            name='MonthlyActiveEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', models.CharField(max_length=255, db_index=True)),
                ('month_for', models.DateField(db_index=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-month_for', 'site', 'course_id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='monthlyactiveenrollment',
            unique_together=set([('site', 'course_id', 'user', 'month_for')]),
        ),
    ]
