# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr_personnel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=55)),
                ('password', models.CharField(max_length=125)),
                ('usertype', models.CharField(default=b'basic', max_length=55, choices=[(b'super_admin', b'Super Admin'), (b'admin', b'Admin'), (b'basic', b'Basic'), (b'guest', b'Guest')])),
                ('email', models.CharField(max_length=125, null=True, blank=True)),
                ('firstname', models.CharField(max_length=55, null=True, blank=True)),
                ('lastname', models.CharField(max_length=55, null=True, blank=True)),
                ('active', models.BooleanField(default=0)),
                ('first_time', models.BooleanField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
                ('profile', models.OneToOneField(null=True, blank=True, to='hr_personnel.Basic')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
