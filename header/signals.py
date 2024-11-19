from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Header

@receiver(pre_save, sender=Header)
def ensure_single_instance(sender, instance, **kwargs):
    if Header.objects.exists() and not instance.pk:
        raise ValueError("Only one Header instance is allowed.")
