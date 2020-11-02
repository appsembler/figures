# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models
import django_countries.fields
from django.conf import settings
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseAccessRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org', models.CharField(db_index=True, max_length=64, blank=True)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(db_index=True, max_length=255, blank=True)),
                ('role', models.CharField(max_length=64, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('created', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('mode', models.CharField(default=b'audit', max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user', 'course_id'),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=255, blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('year_of_birth', models.IntegerField(db_index=True, null=True, blank=True)),
                ('gender', models.CharField(blank=True, max_length=6, null=True, db_index=True, choices=[(b'm', b'Male'), (b'f', b'Female'), (b'o', b'Other/Prefer Not to Say')])),
                ('level_of_education', models.CharField(blank=True, max_length=6, null=True, db_index=True, choices=[(b'p', b'Doctorate'), (b'm', b"Master's or professional degree"), (b'b', b"Bachelor's degree"), (b'a', b'Associate degree'), (b'hs', b'Secondary/high school'), (b'jhs', b'Junior secondary/junior high/middle school'), (b'el', b'Elementary/primary school'), (b'none', b'No formal education'), (b'other', b'Other education')])),
                ('profile_image_uploaded_at', models.DateTimeField(null=True, blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='courseenrollment',
            unique_together=set([('user', 'course_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='courseaccessrole',
            unique_together=set([('user', 'org', 'course_id', 'role')]),
        ),
    ]
