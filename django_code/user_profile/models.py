from __future__ import unicode_literals

import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from program.models import Program
from ourjseditor.util import get_id

def generate_id():
    return get_id()


# Validates a username
def check_username(test_username, current_username):
    return (
        len(test_username) <= 45 and
        test_username != '' and
        not re.search(r"\W", test_username) and
        not (test_username == "logout" or test_username == "login") and
        (test_username == current_username or not User.objects.filter(username=test_username).exists()) and
        not Program.objects.filter(program_id=test_username).exists() and
        not Profile.objects.filter(profile_id=test_username).exists()
    )


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
