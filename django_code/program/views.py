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

def program (request, program_id):
    data_dict = {}

    if program_id == "unsaved":
        data_dict["unsaved"] = True
        data_dict["canEditProgram"] = True

        with open(os.path.join(os.path.dirname(__file__), 'templates.json')) as data_file:
            program_templates = json.load(data_file)
            
            template_name = request.GET.get("template", "blank")
            try:
                template = program_templates[template_name]
            except KeyError:
                template = program_templates["blank"]

            template.pop("description")
                
            data_dict.update(template)
    else:
        try:
            current_program = Program.objects.select_related('user').get(program_id=program_id)
        except Program.DoesNotExist:
            return render(request, "program/404.html", status=404)

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

content_types = {
    "html": "text/plain", # Don't want text/html, because that would be served as a webpage
    "css": "text/css",
    "js": "application/javascript"
}

def program_file (request, program_id, file_type):
    try:
        program = Program.objects.get(program_id=program_id)
    except Program.DoesNotExist:
        return HttpResponse("404: No program found with that id", status=404)

    return HttpResponse(getattr(program, file_type), content_type=content_types[file_type])

def new_program (request):
    with open(os.path.join(os.path.dirname(__file__), 'templates.json')) as data_file:
        program_templates = json.load(data_file)

    for template in program_templates:
        t = program_templates[template];
        program_templates[template] = {
            "title": t["title"],
            "description": t["description"]
        }

    return render(request, "program/new-program.html", { "program_templates": json.dumps(program_templates) })

def fullscreen (request, program_id):
    try:
        program = Program.objects.get(program_id=program_id)
    except Program.DoesNotExist:
        return render(request, "program/404.html", status=404)

    data_dict = {
        "id": program.program_id,

        "js": program.js,
        "html": program.html,
        "css": program.css,
        "title": program.title,
    }

    return render(request, "program/fullscreen.html", { "data_dict": json.dumps(data_dict) })
