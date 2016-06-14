from django.db import models

class mda(models.model):
    name = models.charfield(unique=True, max_length=75)
    user = models.onetoonefield(authuser, models.do_nothing)
    phone_number = models.charfield(32)
