# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import urlparse

from ourjseditor import api
from models import Vote

@api.standardAPIErrors("POST","DELETE")
@api.login_required
def program_vote(request, program_id):
    vote_type = urlparse.parse_qs(request.META["QUERY_STRING"])["type"][0]

    if (vote_type not in ["entertaining", "pretty", "informative"]):
        return api.error("Invalid vote type.")
    try:
        # Look for a vote of the same type cast by the user before
        orig_vote = Vote.objects.get(voted_object_id=program_id, vote_type=vote_type, user_id=request.user.id)

        #If the vote already exists and:
        if (request.method == "DELETE"):
            orig_vote.delete()

        #If the specific vote already exists, do nothing
        return api.succeed()
    except Vote.DoesNotExist:
        #If the vote doesn't already exist
        if (request.method == "POST"):
            Vote.objects.create(user_id=request.user.id, vote_type=vote_type, voted_object_id=program_id)
            return api.succeed({}, status=201) #Return with 201, created

        return api.error("Vote not found.", 404)
