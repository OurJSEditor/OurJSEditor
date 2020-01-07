from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import random

from program.models import Program

#10 character random id. May conflict with notifications
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
def generate_comment_id():
    id_string = ""
    while len(id_string) < 10:
        id_string += random.choice(chars)

    try:
        Comment.objects.get(comment_id=id_string)
        return generate_id()
    except Comment.DoesNotExist:
        return id_string

def get_default_user():
    return User.objects.get(username="admin")

class Comment(models.Model):
    comment_id = models.CharField(primary_key=True, max_length=10, default=generate_comment_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=False) #This program this was posted on
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True) #The comment this is a reply to, or None
    depth = models.IntegerField(blank=False) #0 for comments on programs, 1 for replys to comments on programs, etc.
    reply_count = models.IntegerField(blank=False, default=0)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    edited = models.DateTimeField(blank=True, null=True) #None/null if the comment hasn't been edited

    content = models.TextField(blank=True) #Can be edited
    original_content = models.TextField(blank=True) #Can't be edited. For API and mod access

    def to_dict(self):
        edited = self.edited
        if (edited is not None):
            edited = edited.replace(microsecond=0).isoformat() + "Z",

        parent = self.parent
        if (parent is not None):
            parent = {"id": self.parent_id}

        return {
            "id": self.comment_id,
            "parent": parent,
            "program": {
                "id": self.program_id,
            },
            "author": {
                "id": self.user.profile.profile_id,
                "username": self.user.username,
                "displayName": self.user.profile.display_name,
            },
            "depth": self.depth,
            "replyCount": self.reply_count,
            "created": self.created.replace(microsecond=0).isoformat() + "Z",
            "edited": edited,
            "content": self.content,
            "originalContent": self.original_content,
        }
