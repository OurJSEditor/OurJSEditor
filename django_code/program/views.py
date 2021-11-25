from __future__ import unicode_literals

import json
import re
import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

from program.models import Program, get_programs, PROGRAMS_PER_PAGE
from vote.models import Vote, vote_types

with open(os.path.join(os.path.dirname(__file__), 'templates.json'), "r") as data_file:
    data_str = re.sub(r"\\\n", r"\\n", data_file.read())
    program_templates = json.loads(data_str)


def get_template(key):
    try:
        return next(t for t in program_templates if t["key"] == key)
    except StopIteration:
        raise KeyError(key)


def program(request, program_id):
    data_dict = {}

    if program_id == "unsaved":
        data_dict["unsaved"] = True
        data_dict["canEditProgram"] = True

        template_name = request.GET.get("template", "blank")
        try:
            template = get_template(template_name)
        except KeyError:
            template = get_template("blank")

        template = dict(template) # Clone
        template.pop("description") # Mutates, removing the description property

        data_dict.update(template)
    else:
        try:
            current_program = Program.objects.select_related('user').get(program_id=program_id)
        except Program.DoesNotExist:
            return render(request, "program/404.html", status=404)

        data_dict = current_program.to_dict()
        data_dict["canEditProgram"] = current_program.can_user_edit(request.user)
        data_dict["hasVoted"] = {t: bool(Vote.objects.filter(vote_type=t, voted_object_id=program_id, user_id=request.user.id).count()) for t in vote_types}

    return render(request, "program/index.html", {
        "data_dict": json.dumps(data_dict),
        "MEDIA_URL": settings.MEDIA_URL
    })


def program_list(request, sort):
    if not sort:
        sort = "new" # Default sort. sort is actually passed in as None, so we can't use an argument default

    try:
        programs = get_programs(sort, initial_load=True) # Load and pass one extra program on initial load
    except ValueError:
        return redirect("/programs")

    program_dicts = [p.to_dict(include_code=False) for p in programs]

    return render(request, "program/list.html", {
        "listOptions": json.dumps({
            "initialPrograms": program_dicts,
            "perPage": PROGRAMS_PER_PAGE,
            "sort": sort
        })
    })


CONTENT_TYPES = {
    "html": "text/plain", # Don't want text/html, because that would be served as a webpage
    "css": "text/css",
    "js": "application/javascript"
}


def program_file(request, program_id, file_type):
    try:
        requested_program = Program.objects.get(program_id=program_id)
    except Program.DoesNotExist:
        return HttpResponse("404: No program found with that id", status=404)

    return HttpResponse(getattr(requested_program, file_type), content_type=CONTENT_TYPES[file_type])


def new_program(request):
    template_descriptions = [{
        "title": template["title"],
        "description": template["description"],
        "key": template["key"]
    } for template in program_templates]

    return render(request, "program/new-program.html", {"template_descriptions": json.dumps(template_descriptions)})


def fullscreen(request, program_id):
    try:
        requested_program = Program.objects.get(program_id=program_id)
    except Program.DoesNotExist:
        return render(request, "program/404.html", status=404)

    data_dict = {
        "id": requested_program.program_id,

        "js": requested_program.js,
        "html": requested_program.html,
        "css": requested_program.css,
        "title": requested_program.title,
    }

    return render(request, "program/fullscreen.html", {
        "data_dict": json.dumps(data_dict),
        "MEDIA_URL": settings.MEDIA_URL
    })
