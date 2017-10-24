# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from models import Comment
from program.models import Program
from ourjseditor import api

"""
    /program/PRO_ID/comments/new (POST)
    /program/PRO_ID/comments/COM_ID (GET, PATCH, DELETE)
    /comments/COM_ID (GET, PATCH, DELETE)
"""


# /program/PRO_ID/comments/new
@api.standardAPIErrors("POST")
def new_comment(request, program_id):
    data = json.loads(request.body)

    # A JSON of `null` gets parsed into a Python of `None`
    # If parent isn't passed, KeyError, caught by standardAPIErrors
    parent_comment = data["parent"]
    if (parent_comment is None):
        depth = 0
    else:
        parent_comment = Comment.objects.get(parent_comment)
        depth = parent_comment.depth + 1

    comment = Comment.objects.create(
        user = request.user,
        program = Program.objects.get(program_id = program_id),
        parent = parent_comment,
        depth = depth,
        content = data["content"],
        original_content = data["content"],
    )

    response = api.succeed({"id": comment.comment_id}, status=201)
    response["Location"] = "/program/{0}#comment_{1}".format(comment.program.program_id, comment.comment_id)
    return response
