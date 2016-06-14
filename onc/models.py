from django.db import models

class Authuser(models.model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.BooleanField()
    # username = models.charfield(unique=true, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(unique=True, max_length=75)
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()


