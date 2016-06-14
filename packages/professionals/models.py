from django.db import models

class skill(models.model):
    title = models.charfield(unique=True, max_length=75)


class professional(models.model):
    user = models.onetoonefield(authuser, models.do_nothing)
    organizations = models.manytomanyfield(organization, models.do_nothing)
    skills = models.manytomanyfield(skill, models.do_nothing)
    location = models.charfield(max_length=64) # one of 36 states
    phone_number = models.charfield(32)
    institution =  models.charfield(64)
