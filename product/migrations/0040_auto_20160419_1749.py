# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 16:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0039_ordermembership_voidedbyseller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermembership',
            name='time_ordered',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
