# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Vendor

@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created:
        Vendor.objects.create(user=instance)
