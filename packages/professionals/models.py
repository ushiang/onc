from django.db import models

from onc.models import Authuser
from packages.organizations.models import Organization

class Skill(models.Model):
    title = models.CharField(unique=True, max_length=75)


class Professional(models.Model):
    user = models.OneToOneField(Authuser, models.DO_NOTHING())
    organizations = models.ManyToManyField(Organization, models.DO_NOTHING())
    skills = models.ManyToManyField(Skill, models.DO_NOTHING())
    location = models.CharField(max_length=64) # one of 36 states
    phone_number = models.CharField(32)
    institution = models.CharField(64)
