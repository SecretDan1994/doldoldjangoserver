# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 07:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_remove_sidebarentry_faicon'),
    ]

    operations = [
        migrations.AddField(
            model_name='sidebarentry',
            name='faicon',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='sidebarentry',
            name='styling',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
