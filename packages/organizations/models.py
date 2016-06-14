from django.db import models

from packages.products_services.models import Service

class Organization(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=200)
    tin_number = models.CharField(max_length=64) #tax number
    number_of_staff = models.IntegerField()
    phone_number = models.CharField(32)
    services = models.ManyToManyField(Service, models.DO_NOTHING)
