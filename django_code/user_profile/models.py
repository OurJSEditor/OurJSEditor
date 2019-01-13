from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def generate_id():
    from ourjseditor.funcs import get_id

    return get_id();

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # max_length is not enforced automatically
    bio = models.TextField(max_length=500, blank=True)
    # Max length of 45 (is enforced for CharField). Not required, but should always be filled.
    display_name = models.CharField(max_length=45, blank=True)
    # id. 6 digits, doesn't overlap with program ids
    profile_id = models.CharField(primary_key=True, max_length=6, default=generate_id)
    subscriptions = models.ManyToManyField("self", symmetrical=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
