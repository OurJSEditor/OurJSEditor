from __future__ import unicode_literals

import json

from ourjseditor import api
from program.models import Program
from .models import Vote, vote_types


# /api/program/PRO_ID/vote
@api.StandardAPIErrors("POST", "DELETE")
@api.login_required
def program_vote(request, program_id):
    vote_type = json.loads(request.body)["type"]

    if vote_type not in vote_types:
        return api.error("Invalid vote type.")
    try:
        voted_program = Program.objects.get(program_id=program_id)
        orig_votes = getattr(voted_program, vote_type + "_votes")

        # Look for a vote of the same type cast by the user before
        orig_vote = Vote.objects.get(voted_object_id=program_id, vote_type=vote_type, user_id=request.user.id)

        # If the vote already exists and:
        if request.method == "DELETE":
            setattr(voted_program, vote_type + "_votes", orig_votes - 1)
            voted_program.save()

            orig_vote.delete()
            return api.succeed()
        # If the specific vote already exists, and you're posting it again
        elif request.method == "POST":
            # 403 Forbidden, is used here beacuse there is no authentication that would allow the request
            return api.error("Already voted.", status=403)
    except Vote.DoesNotExist:
        # If the vote doesn't already exist
        if request.method == "POST":
            Vote.objects.create(user_id=request.user.id, vote_type=vote_type, voted_object_id=program_id)

            setattr(voted_program, vote_type + "_votes", orig_votes + 1)
            voted_program.save()

            # Return with 201, created
            return api.succeed({}, status=201)
        elif request.method == "DELETE":
            return api.error("Vote not found.", 404)
