

from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField

class UserProfile(models.Model):
    '''
    the production model is student.models.UserProfile
    '''
    user = models.OneToOneField(User, unique=True, db_index=True, related_name='profile')
    name = models.CharField(blank=True, max_length=255, db_index=True)
    country = CountryField(blank=True, null=True)
