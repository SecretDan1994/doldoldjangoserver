# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-08 12:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('order',), 'permissions': (('view_category', 'Can view category'),), 'verbose_name_plural': 'Categories'},
        ),
    ]
