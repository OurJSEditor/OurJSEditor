# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Notif(models.Model):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE) #The user that gets the notifcation
    link = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    description = models.CharField(max_length=140) #50 for our message + 45 for a display name + 45 for a program title
    preview = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
