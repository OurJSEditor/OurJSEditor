# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from comment.models import Comment

# Create your models here.
class Notif(models.Model):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE) #The user that gets the notifcation
    link = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    description = models.CharField(max_length=140) #50 for our message + 45 for a display name + 45 for a program title
    source_comment = models.ForeignKey(Comment, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        notif_dict = {
            "link": self.link,
            "isRead": self.is_read,
            "description": self.description,
            "created": self.created.replace(microsecond=0).isoformat() + "Z",
        }

        if (self.source_comment):
            notif_dict["sourceComment"] = {
                "id": self.source_comment_id,
            }
            notif_dict["preview"] = self.source_comment.content[:100]

        return notif_dict
