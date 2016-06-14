# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='lid',
            field=models.CharField(default=b'dmc', max_length=25),
        ),
        migrations.AlterField(
            model_name='users',
            name='sys',
            field=models.CharField(default=b'geoqinetiq', max_length=25),
        ),
    ]
