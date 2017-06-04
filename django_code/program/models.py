# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random

from django.db import models

from django.contrib.auth.models import User
from user_profile.models import Profile

def generate_id():
    chars = "abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

    id_string = ""
    while len(id_string) < 6:
        id_string += random.choice(chars)

    try:
        # Try to get a program with the current id
        Program.objects.get(program_id=id_string)
        # If we don't error there is a program with this id already. Re-generate id
        return generate_id()
    except Program.DoesNotExist:
        return id_string

def get_default_user_profile():
    return User.objects.get(username="admin").profile

class Program(models.Model):
    program_id = models.CharField(primary_key=True, max_length=6, default=generate_id)
    user = models.ForeignKey('user_profile.Profile', on_delete=models.CASCADE, default=get_default_user_profile)
    title = models.CharField(max_length=45, default="Program")
    html_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    css_content = models.TextField(blank=True)
