from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    if created and instance.is_staff and profile.role == UserProfile.ROLE_SUBMITTER:
        profile.role = UserProfile.ROLE_ADMIN
        profile.save()

