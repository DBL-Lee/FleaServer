from __future__ import unicode_literals

from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=20, blank=True, default='')
    mainimage = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    location = models.CharField(max_length=5)
    gps = models.CharField(max_length=40)
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=10)
    amount = models.IntegerField()
    category = models.ForeignKey('SecondaryCategory', on_delete=models.SET_NULL,null=True)
    postedTime = models.DateTimeField(auto_now_add=True)
    originalPrice = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    brandNew = models.NullBooleanField()
    bargain = models.NullBooleanField()
    exchange = models.NullBooleanField()
    description = models.TextField(blank=True, default='')

class ImageUUID(models.Model):
	product = models.ForeignKey('Product',on_delete=models.CASCADE,related_name='images')
	uuid = models.CharField(max_length=40)

class Version(models.Model):
    version = models.IntegerField()

class PrimaryCategory(models.Model):
    title = models.CharField(max_length=10)
    icon = models.CharField(max_length=40, blank=True, default='')
    version = models.ForeignKey(Version,default=1)

class SecondaryCategory(models.Model):
    title = models.CharField(max_length=10)
    primaryCategory = models.ForeignKey(PrimaryCategory, related_name='secondary')
