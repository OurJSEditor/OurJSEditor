from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django import db

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
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                if (len(data["title"]) > 45):
                    return HttpResponse('{"creationSuccess":false, "error":"Title length exceeds maximum characters."}', content_type="application/json", status=400)

                program = Program.objects.create(
                    user = request.user,
                    title = data["title"],
                    html = data["html"],
                    js = data["js"],
                    css = data["css"],
                )

                response = HttpResponse('{"creationSuccess":true}', content_type="application/json", status=201)
                response["Location"] = "/program/" + program.program_id
                return response

            # KeyError if user-passed dict is missing something we want
            except KeyError as err:
                return HttpResponse('{"creationSuccess":false, "error":"Missing data for %s."}' % str(err), content_type="application/json", status=400)
            # db.Error if the db rejects what we try to include; TypeError for other things, e.g. title is an int and len() fails or data is a string and ["title"] fails
            except (db.Error, TypeError):
                return HttpResponse('{"creationSuccess":false, "error":"Invalid data."}', content_type="application/json", status=400)
            # ValueError if parsing the JSON failed
            except ValueError:
                return HttpResponse('{"creationSuccess":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)
        else:
            return HttpResponse('{"creationSuccess":false,"error":"Not logged in."}', content_type="application/json", status=403)
    else:
        return HttpResponse("The method " + request.method + " is not allowed for the requested URL.", status=405)

def program(request, program_id):
    try:
        requested_program = Program.objects.get(program_id=program_id)
        if (request.method == "GET"):
            program_dict = dict(
                author_username = requested_program.user.username,
                id = requested_program.program_id,
                title = requested_program.title,
                css = requested_program.css,
                js = requested_program.js,
                html = requested_program.html
            )
            return HttpResponse(json.dumps(program_dict), content_type="application/json", status=200)
        elif (request.method == "PATCH"):
            try:
                data = json.loads(request.body)

                if request.user != requested_program.user:
                    return HttpResponse('{"success":false,"error":"Not authorized."}', content_type="application/json", status=403)

                valid_props = ["html", "js", "css", "title"]
                for prop in valid_props:
                    if prop in data:
                        setattr(requested_program, prop, data[prop])

                requested_program.save()

                return HttpResponse('', status=204)
            except ValueError:
                return HttpResponse('{"success":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)
        elif (request.method == "DELETE"):
            if request.user != requested_program.user:
                return HttpResponse('{"success":false,"error":"Not authorized."}', content_type="application/json", status=403)

            requested_program.delete()

            return HttpResponse('', status=204)
        else:
            return HttpResponse("The method " + request.method + " is not allowed for the requested URL.", status=405)
    except Program.DoesNotExist:
        return HttpResponse("No program exists with that id.", status=404)

def error(request):
    return HttpResponse('null', content_type="application/json", status=400)
