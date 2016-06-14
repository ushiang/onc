from django.db import models

class organization(models.model):
    name = models.charfield(max_length=128)
    address = models.charfield(max_length=200)
    tin_number = models.charfield(max_length=64) #tax number
    number_of_staff = models.integerfield()
    phone_number = models.charfield(32)
    services = models.manytomanyfield(service, models.do_nothing)
