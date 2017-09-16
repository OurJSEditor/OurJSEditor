# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from program.models import Program

import json

# Create your views here.
def program (request, program_id):
    data_dict = dict()

    if program_id == "new":
        data_dict["new"] = True
        data_dict["canEditProgram"] = True
    else:
        try:
            current_program = Program.objects.select_related('user').get(program_id=program_id)

            data_dict["id"] = program_id
            data_dict["title"] = current_program.title
            data_dict["js"] = current_program.js
            data_dict["css"] = current_program.css
            data_dict["html"] = current_program.html
            data_dict["created"] = current_program.created.replace(microsecond=0).isoformat() + "Z"
            data_dict["canEditProgram"] = (current_program.user == request.user)
            data_dict["author"] = dict(
                username=current_program.user.username,
                displayName=current_program.user.profile.display_name,
                id=current_program.user.profile.profile_id
            )
        except Program.DoesNotExist:
            return HttpResponse("404: No program found with that id", status=404)

    return render(request, "program/index.html", {"data_dict": json.dumps(data_dict)})
