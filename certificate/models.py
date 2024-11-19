from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Certificate(models.Model):
    certificate = models.TextField(default='')
    description = models.TextField(default='', blank=True)
    year = models.IntegerField(default=now().year, blank=True)   
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
