# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-17 19:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0038_ordermembership_ongoing'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermembership',
            name='voidedbyseller',
            field=models.NullBooleanField(),
        ),
    ]
