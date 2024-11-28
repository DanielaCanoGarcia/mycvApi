from django.db import models
from django.conf import settings

class Header(models.Model):
    name = models.CharField(default='')
    description = models.TextField(blank=True, null=True)
    urlImage = models.URLField(blank=True, null=True) 
    email = models.EmailField(default='')
    telephone = models.CharField(blank=True, null=True)
    ubication = models.TextField(blank=True, null=True)
    redSocial = models.TextField(blank=True, null=True)
    posted_by = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)