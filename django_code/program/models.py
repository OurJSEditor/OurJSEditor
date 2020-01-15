from __future__ import unicode_literals

from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

import datetime

from vote.models import vote_types

def generate_id():
    from ourjseditor.funcs import get_id
    return get_id()

def get_default_user():
    return User.objects.get(username="admin")

def get_image_path(program, _):
    return "program/{}.png".format(program.program_id)

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name

class Program(models.Model):
    program_id = models.CharField(primary_key=True, max_length=6, default=generate_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True) #The program this is a Spin-off of
    collaborators = models.ManyToManyField(User, related_name="+")

    last_published = models.DateTimeField(blank=True, null=True)
    published_message = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to=get_image_path, storage=OverwriteStorage(), default="program/nophoto.png")

    title = models.CharField(max_length=45, default="Program")
    html= models.TextField(blank=True)
    js = models.TextField(blank=True)
    css = models.TextField(blank=True)

    entertaining_votes = models.IntegerField(default=0)
    artistic_votes = models.IntegerField(default=0)
    informative_votes = models.IntegerField(default=0)
    
    def can_user_edit(self, user):
        return (
            self.user == user or
            self.collaborators.filter(id=user.id).exists()
        )
    
    def to_dict(self, include_code=True):
        if self.last_published:
            last_published = self.last_published.replace(microsecond=0).isoformat() + "Z"
        else:
            last_published = None

        parent = self.parent
        if (parent is not None):
            parent = {
                "id": self.parent_id,
                "title": self.parent.title
            }

        program_dict = {
            "id": self.program_id,
            "author": {
                "id": self.user.profile.profile_id,
                "displayName": self.user.profile.display_name,
                "username": self.user.username,
            },
            "created": self.created.replace(microsecond=0).isoformat() + "Z",
            "parent": parent,

            "title": self.title,

            "lastPublished": last_published,
            "thumbnailUrl": self.image.url,

            "collaborators": list(self.collaborators.values_list("profile__profile_id", flat=True)),
            
            "votes": dict([(t, getattr(self, t + "_votes")) for t in vote_types])
        }

        if (include_code):
            program_dict["js"] = self.js
            program_dict["html"] = self.html
            program_dict["css"] = self.css

        return program_dict

# Called from:
#   - program/view.program_list; get the first 20 programs by a sort
#   - program/api.program_list; get programs with offset and limit
#   - view and api for user program list, need sort, offset, and limit options
#   - home page, getting 3 most recently edited programs (limit, sort, user, unpublished), 3 popular programs, 4 programs from subscriptions
#   TODO: to get spin-offs of a given program

# filters is a Q object
# e.g. get_programs("top", Q(author=User.objects.get(username="Matthias")), published_only=True)
def get_programs(sort, filters=None, offset=0, limit=20, published_only=True):
    programs = Program.objects

    if (published_only):
        programs = programs.filter(last_published__isnull=False)

    if (filters):
        programs = programs.filter(filters)

    # Maps public names (top, new, hot, entertaining, etc.) to names the database understands (total_votes, created, hotness?, entertaining_votes)
    if (sort == "top"):
        programs = programs.annotate(total_votes=F("informative_votes") + F("artistic_votes") + F("entertaining_votes"))
        sort = "-total_votes"
    elif (sort == "new"):
        sort = "-last_published" if published_only else "-created"
    elif (sort in vote_types):
        sort = "-" + sort + "_votes"
    else:
        raise ValueError("Invalid Sort.")

    programs = programs.order_by(sort)[offset:offset+limit]

    return programs
