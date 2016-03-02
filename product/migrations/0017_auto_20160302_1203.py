# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 12:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_product_mainimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='latitude',
            field=models.FloatField(default=51.758562344),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='longitude',
            field=models.FloatField(default=-1.267191654),
            preserve_default=False,
        ),
    ]
