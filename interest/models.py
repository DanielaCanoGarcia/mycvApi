from django.db import models
from django.conf import settings

class Interest(models.Model):
    interest = models.CharField(max_length=100, default='')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
