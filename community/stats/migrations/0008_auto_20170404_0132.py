# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 01:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0007_auto_20170404_0132'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serverlog',
            old_name='tags',
            new_name='tag',
        ),
    ]
