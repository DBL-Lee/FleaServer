# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-14 15:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0035_auto_20160414_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_ordered', models.DateField(auto_now_add=True)),
                ('amount', models.IntegerField()),
                ('accepted', models.NullBooleanField()),
                ('finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='boughtBy',
        ),
        migrations.RemoveField(
            model_name='product',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='product',
            name='orderer',
        ),
        migrations.AddField(
            model_name='product',
            name='soldAmount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ordermembership',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
        migrations.AddField(
            model_name='ordermembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
