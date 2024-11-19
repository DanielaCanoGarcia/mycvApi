from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils.timezone import now


class WorkExperience(models.Model):
    city       = models.TextField(default='')
    year_start = models.IntegerField(default=now().year, blank=True) 
    year_end   = models.IntegerField(default=now().year, blank=True)  
    work       = models.TextField(default=dict, blank=True, null=True)
    position   = models.TextField(default=dict, blank=True, null=True)
    achievments = models.JSONField(default=dict, blank=True, null=True)
    posted_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)