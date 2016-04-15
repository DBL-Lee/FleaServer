# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-14 12:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0033_auto_20160403_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='orderer',
            field=models.ManyToManyField(related_name='orderedProducts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='product',
            name='buyer',
        ),
        migrations.AddField(
            model_name='product',
            name='buyer',
            field=models.ManyToManyField(related_name='boughtProducts', to=settings.AUTH_USER_MODEL),
        ),
    ]
