# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

import datetime

from vote.models import vote_types

def generate_id():
    from ourjseditor.funcs import get_id
    return get_id();

def get_default_user():
    return User.objects.get(username="admin")

class Program(models.Model):
    program_id = models.CharField(primary_key=True, max_length=6, default=generate_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=45, default="Program")
    html= models.TextField(blank=True)
    js = models.TextField(blank=True)
    css = models.TextField(blank=True)
    entertaining_votes = models.IntegerField(default=0)
    artistic_votes = models.IntegerField(default=0)
    informative_votes = models.IntegerField(default=0)

    def to_dict(self):
        return {
            "id": self.program_id,
            "author": {
                "id": self.user.profile.profile_id,
                "displayName": self.user.profile.display_name,
                "username": self.user.username,
            },
            "created": self.created.replace(microsecond=0).isoformat() + "Z",
            "js": self.js,
            "html": self.html,
            "css": self.css,
            "title": self.title,
            "votes": dict([(t, getattr(self, t + "_votes")) for t in vote_types])
        }
