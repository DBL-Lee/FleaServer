# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 06:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_myuser'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]
