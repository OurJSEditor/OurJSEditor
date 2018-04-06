# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse
from program.models import Program
from vote.models import Vote, vote_types

import json
import os

key_func_mapping = {
    "new": "created",
    "top": lambda program: sum([getattr(program, t + "_votes") for t in vote_types])
}
for t in vote_types:
    key_func_mapping[t] = t + "_votes"

# Create your views here.
def program (request, program_id):
    data_dict = {}

    if program_id == "new":
        data_dict["new"] = True
        data_dict["canEditProgram"] = True

        with open(os.path.join(os.path.dirname(__file__), 'default.json')) as data_file:
            data_dict.update(json.load(data_file))
    else:
        try:
            current_program = Program.objects.select_related('user').get(program_id=program_id)
        except Program.DoesNotExist:
            return HttpResponse("404: No program found with that id", status=404)

        data_dict = current_program.to_dict()
        data_dict["canEditProgram"] = (current_program.user == request.user)
        data_dict["hasVoted"] = dict([(t, bool(Vote.objects.filter(vote_type=t, voted_object_id=program_id, user_id=request.user.id).count())) for t in vote_types])

    return render(request, "program/index.html", {"data_dict": json.dumps(data_dict)})

def program_list (request, sort):
    if (not sort):
        sort = "new" # Default sort. sort is actually passed in as None, so we can't use an argument default

    if (sort not in key_func_mapping):
        return redirect("/programs")

    key_func = key_func_mapping[sort]
    if (type(key_func) is unicode):
        key_func = lambda program: getattr(program, key_func_mapping[sort])

    programs = sorted(Program.objects.all(), reverse=True, key=key_func)[:20]

    return render(request, "program/list.html", {"programs": programs})
