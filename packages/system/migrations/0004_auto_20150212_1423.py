# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_auto_20150212_1239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='msg',
            new_name='code',
        ),
    ]
