from __future__ import unicode_literals

import random
from django.db import models
from django.contrib.auth.models import User

from comment.models import Comment
from program.models import Program

#10 character random id. May conflict with comments
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
def generate_notif_id():
    id_string = ""
    while len(id_string) < 10:
        id_string += random.choice(chars)

    try:
        Notif.objects.get(notif_id=id_string)
        return generate_id()
    except Notif.DoesNotExist:
        return id_string

# Create your models here.
class Notif(models.Model):
    notif_id = models.CharField(primary_key=True, max_length=10, default=generate_notif_id)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE) #The user that gets the notifcation
    link = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    description = models.CharField(max_length=140) #50 for our message + 45 for a display name + 45 for a program title
    source_comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE)
    source_program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        notif_dict = {
            "id": self.notif_id,
            "link": self.link,
            "isRead": self.is_read,
            "description": self.description,
            "created": self.created.replace(microsecond=0).isoformat() + "Z",
            "preview": "" # Gets overwritten if there's a source comment or program
        }

        if (self.source_comment):
            notif_dict["sourceComment"] = {
                "id": self.source_comment_id,
            }
            notif_dict["preview"] = self.source_comment.content[:100]

        if self.source_program:
            notif_dict["sourceProgram"] = {
                "id": self.source_program_id,
            }
            notif_dict["preview"] = self.source_program.published_message[:100]

        return notif_dict
