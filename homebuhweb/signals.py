from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        group, _ = Group.objects.get_or_create(name='Users')
        instance.groups.add(group)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        group, _ = Group.objects.get_or_create(name='Users')
        instance.groups.add(group)


@receiver(post_delete, sender=User)
def delete_profile(sender, instance, **kwargs):
    try:
        instance.profile.delete()
    except Profile.DoesNotExist:
        pass

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
