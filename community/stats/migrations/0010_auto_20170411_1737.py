# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-11 17:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0009_auto_20170404_0156'),
    ]

    operations = [
        migrations.AddField(
            model_name='logtag',
            name='spy',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='serverlog',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.LogTag'),
        ),
    ]
