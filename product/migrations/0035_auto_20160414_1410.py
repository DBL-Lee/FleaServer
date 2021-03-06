# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-14 14:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0034_auto_20160414_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='boughtBy',
            field=models.ManyToManyField(related_name='boughtProducts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='buyer',
            field=models.ManyToManyField(related_name='pendingProducts', to=settings.AUTH_USER_MODEL),
        ),
    ]
