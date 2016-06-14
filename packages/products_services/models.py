from django.db import models

class Service(models.model):
    title = models.CharField(unique=True, max_length=75)

