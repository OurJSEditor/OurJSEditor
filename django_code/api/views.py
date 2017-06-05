from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

import json

from program.models import Program

# Create your views here.

def username_available(request):
    username = request.GET.get("username", "")
    if (username == ""):
        return error(request)
    try:
        user = User.objects.get(username=username)
        return HttpResponse('{"username_available":false}', content_type="application/json", status=200)
    except User.DoesNotExist:
        return HttpResponse('{"username_available":true}', content_type="application/json", status=200)

def new_program(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if request.user.is_authenticated:
                program = Program.objects.create(
                    user = request.user.profile,
                    title = data["title"],
                    html_content = data["html"],
                    js_content = data["js"],
                    css_content = data["css"],
                )

                response = HttpResponse('{"creationSuccess":true}', content_type="application/json", status=201)
                response["Location"] = "/program/" + program.program_id
                return response
            else:
                return HttpResponse('{"creationSuccess":false,"error":"Not logged in."}', content_type="application/json", status=403)
        except ValueError:
            # Catch and return 400 on malformed JSON
            return HttpResponse('{"creationSuccess":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)
    else:
        return HttpResponse("The method " + request.method + " is not allowed for the requested URL.", status=405)

def view_program(request, program_id):
    try:
        requested_program = Program.objects.get(program_id=program_id)
        program_dict = dict(
            author_username = requested_program.user.user.username,
            id = requested_program.program_id,
            title = requested_program.title,
            css = requested_program.css_content,
            js = requested_program.js_content,
            html = requested_program.html_content
        )
        return HttpResponse(json.dumps(program_dict), content_type="application/json", status=200)
    except Program.DoesNotExist:
        return HttpResponse("No program exists with that id.", status=404)

def error(request):
    return HttpResponse('null', content_type="application/json", status=400)
