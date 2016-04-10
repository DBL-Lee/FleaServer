from __future__ import unicode_literals

from django.db import models

class EaseToken(models.Model):
    token = models.CharField(max_length=100)
    expires_in = models.DateTimeField()
    application = models.CharField(max_length=50)
