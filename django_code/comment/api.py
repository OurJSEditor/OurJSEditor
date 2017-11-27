# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import datetime

from models import Comment
from program.models import Program
from ourjseditor import api

# /program/PRO_ID/comment/new
@api.standardAPIErrors("POST")
@api.login_required
def new_comment(request, program_id):
    data = json.loads(request.body)

    # A JSON of `null` gets parsed into a Python of `None`
    # If parent isn't passed, KeyError, caught by standardAPIErrors
    parent_comment = data["parent"]
    if (parent_comment is None):
        depth = 0
    else:
        try:
            parent_comment = Comment.objects.get(comment_id=parent_comment, program_id=program_id)
        except Comment.DoesNotExist:
            return api.error("Invalid comment parent")
        depth = parent_comment.depth + 1

    if (depth > 1):
        return api.error("Comments have gone too deep!")

    if (parent_comment is not None):
        parent_comment.reply_count += 1
        parent_comment.save()

    comment = Comment.objects.create(
        user = request.user,
        program = Program.objects.get(program_id = program_id),
        parent = parent_comment,
        depth = depth,
        content = data["content"],
        original_content = data["content"],
    )

    response = api.succeed({"id": comment.comment_id}, status=201)
    response["Location"] = "/program/{0}#comment-{1}".format(comment.program.program_id, comment.comment_id)
    return response

# /api/program/PRO_ID/comment/COMMENT_ID
# /api/comment/COMMENT_ID
@api.standardAPIErrors("GET", "PATCH", "DELETE")
def comment(request, *args):
    if (len(args) == 1):
        comment_id = args[0]

        requested_comment = Comment.objects.get(comment_id=comment_id)
    elif (len(args) == 2):
        program_id = args[0]
        comment_id = args[1]

        requested_comment = Comment.objects.get(program_id=program_id, comment_id=comment_id)

    if (request.method == "GET"):
        return api.succeed(requested_comment.to_dict())

    # Comment editing!
    elif (request.method == "PATCH"):
        data = json.loads(request.body)

        if request.user != requested_comment.user:
            return api.error("Not authorized.", status=401)

        requested_comment.content = data["content"]
        requested_comment.edited = datetime.datetime.now()

        requested_comment.save()

        return api.succeed({})

    elif (request.method == "DELETE"):
        if request.user != requested_comment.user:
            return api.error("Not authorized.", status=401)

        parent = requested_comment.parent
        if (parent is not None):
            parent.reply_count -= 1;
            parent.save();

        requested_comment.delete()

        return api.succeed({})

# Endpoint for what KA calls replies, i.e. comments on comments, i.e. comments with a depth > 0
# Note: POST requests for these are still made to /api/program/PRO_ID/comments, just with "parent": "COMMENT_ID"
# /api/program/PRO_ID/comment/COMMENT_ID/comments
# /api/comment/COMMENT_ID/comments
@api.standardAPIErrors("GET")
def comment_comments(request, *args):
    if (len(args) == 1):
        comment_id = args[0]

        comments = Comment.objects.select_related("user__profile").filter(parent__comment_id=comment_id)
    elif (len(args) == 2):
        program_id = args[0]
        comment_id = args[1]

        comments = Comment.objects.select_related("user__profile").filter(program_id=program_id, parent__comment_id=comment_id)

    comments = list(comments)
    return api.succeed({
        "comments": map(lambda c: c.to_dict(), comments)
    })

# /program/PRO_ID/comments
@api.standardAPIErrors("GET")
def program_comments(request, program_id):
    comments = list(Comment.objects.select_related("user__profile").filter(program_id=program_id, depth=0))
    return api.succeed({
        "comments": map(lambda c: c.to_dict(), comments)
    })
