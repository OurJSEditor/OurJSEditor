from __future__ import unicode_literals

from django.db import models

vote_types = ["entertaining", "artistic", "informative"]

# Create your models here.
class Vote(models.Model):
    voted_object_id = models.CharField(max_length=10)
    cast_time = models.DateTimeField(auto_now_add=True, blank=False)
    vote_type = models.CharField(max_length=12) # one of "entertaining" "artistic" or "informative" for programs
    user_id = models.IntegerField() # Basically a ForeignKey, but we don't need to access any properties of it
