from django.db import models
from onc.models import Authuser

class Mda(models.Model):
    name = models.CharField(unique=True, max_length=75)
    user = models.OneToOneField(Authuser, models.DO_NOTHING())
    phone_number = models.CharField(32)
