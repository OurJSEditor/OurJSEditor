# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from models import Comment
from program.models import Program
from ourjseditor import api

"""
    /program/PRO_ID/comments (GET)
    /program/PRO_ID/comment/new (POST)
    /program/PRO_ID/comment/COM_ID (GET, PATCH, DELETE)
    /comment/COM_ID (GET, PATCH, DELETE)
"""


# /program/PRO_ID/comment/new
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

# /api/program/PRO_ID/comment/COMMENT_ID
# /api/comment/COMMENT_ID
@api.standardAPIErrors("GET", "PATCH", "DELETE")
def comment(request, *args):
    if (request.method == "GET"):
        if (len(args) == 1):
            comment_id = args[0]

            requested_comment = Comment.objects.get(comment_id=comment_id)
        elif (len(args) == 2):
            program_id = args[0]
            comment_id = args[1]

            requested_comment = Comment.objects.get(program_id=program_id, comment_id=comment_id)

        edited = requested_comment.edited
        if (edited is not None):
            edited = edited.replace(microsecond=0).isoformat() + "Z",

        parent = requested_comment.parent
        if (parent is not None):
            parent = {"id": parent.comment_id}

        return api.succeed({
            "id": requested_comment.comment_id,
            "parent": parent,
            "program": {
                "id": requested_comment.program.program_id,
            },
            "depth": requested_comment.depth,
            "replyCount": requested_comment.reply_count,
            "created": requested_comment.created.replace(microsecond=0).isoformat() + "Z",
            "edited": edited,
            "content": requested_comment.content,
            "original_content": requested_comment.original_content,
        })
    


def program_comments(request, program_id):
    return api.succeed()
