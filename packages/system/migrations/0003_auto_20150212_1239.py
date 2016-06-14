# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20140929_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('alias', models.CharField(max_length=25)),
                ('author', models.CharField(max_length=55, null=True, blank=True)),
                ('version', models.CharField(max_length=12, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('msg', models.TextField()),
                ('number', models.IntegerField(default=1)),
                ('pattern', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivilegeManifest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('alias', models.CharField(max_length=25)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
                ('module', models.ForeignKey(related_name='module_privilege_manifest', to='system.Module')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivilegeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
                ('manifest', models.ForeignKey(related_name='manifest_privilege_user', to='system.PrivilegeManifest')),
                ('user', models.ForeignKey(related_name='user_privilege', to='system.Users')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=55)),
                ('alias', models.CharField(max_length=55)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
                ('module', models.ForeignKey(related_name='module_user_class', to='system.Module')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserClassTies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('sys', models.CharField(default=b'dmc', max_length=25)),
                ('lid', models.CharField(default=b'shareware', max_length=25)),
                ('user', models.ForeignKey(related_name='users_user_class', to='system.Users')),
                ('user_class', models.ForeignKey(related_name='user_class_users', to='system.UserClass')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='privilege',
            name='manifest',
            field=models.ForeignKey(related_name='manifest_privilege', to='system.PrivilegeManifest'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='privilege',
            name='user_class',
            field=models.ForeignKey(related_name='user_class_privilege', to='system.UserClass'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='lid',
            field=models.CharField(default=b'shareware', max_length=25),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='sys',
            field=models.CharField(default=b'dmc', max_length=25),
            preserve_default=True,
        ),
    ]
