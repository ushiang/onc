from django.db import models

class authuser(models.model):
    password = models.charfield(max_length=128)
    last_login = models.datetimefield()
    is_superuser = models.booleanfield()
    # username = models.charfield(unique=true, max_length=30)
    first_name = models.charfield(max_length=30)
    last_name = models.charfield(max_length=30)
    email = models.charfield(unique=True, max_length=75)
    is_active = models.booleanfield()
    date_joined = models.datetimefield()


