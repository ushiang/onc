from django.db import models

class service(models.model):
    title = models.charfield(unique=True, max_length=75)

