from django.db import models
from django.conf import settings

class Header(models.Model):
    name       = models.TextField(default='')
    description       = models.TextField(default=dict, blank=True, null=True)
    urlImage   = models.TextField(default=dict, blank=True, null=True)
    email       = models.TextField(default='')
    telephone       = models.TextField(default=dict, blank=True, null=True)
    ubication   = models.TextField(default=dict, blank=True, null=True)
    redSocial   = models.TextField(default=dict, blank=True, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
