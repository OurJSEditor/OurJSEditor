from ourjseditor import api
from ourjseditor.funcs import base64toImageFile, get_as_int

import json
import datetime

from django.template.defaultfilters import escape

from .models import Program, get_programs
from vote.models import vote_types
from notification.models import Notif

#/api/program/new
@api.standardAPIErrors("POST")
@api.login_required
def new_program(request):
    data = json.loads(request.body)
    if (len(data["title"]) > 45):
        return api.error("Title length exceeds maximum characters.")

    program = Program.objects.create(
        user = request.user,
        title = data["title"],
        html = data["html"],
        js = data["js"],
        css = data["css"],
    )

    response = api.succeed({ "id": program.program_id }, status=201)
    response["Location"] = "/program/" + program.program_id
    return response

#/api/program/PRO_ID/forks
@api.standardAPIErrors("POST")
def forks(request, program_id):
    if (request.method == "POST"):
        if (not request.user.is_authenticated):
            return api.error("Not logged in.", status=401)

        parent_program = Program.objects.get(program_id=program_id)

        data = json.loads(request.body)
        if (len(data["title"]) > 45):
            return api.error("Title length exceeds maximum characters.")

        program = Program.objects.create(
            user = request.user,
            parent = parent_program,
            title = data["title"],
            html = data["html"],
            js = data["js"],
            css = data["css"],
        )

        if (parent_program.user != program.user):
            Notif.objects.create(
                target_user = parent_program.user,
                link = "/program/" + program.program_id,
                description = "<strong>{0}</strong> created a fork of your program, <strong>{1}</strong>".format(
                    escape(request.user.profile.display_name), escape(parent_program.title)),
            )

        response = api.succeed({ "id": program.program_id }, status=201)
        response["Location"] = "/program/" + program.program_id
        return response
        
#/api/program/collaborators
@api.standardAPIErrors("POST") # TODO: GET?
def collaborators(request, program_id):
    # {user:{id:""}}
    # {user:{username:""}}
    # the request is unauthed
    # Check if collaborators is already a collab
    # or is the author

    pass
    
#/api/program/collaborators/USER_ID
@api.standardAPIErrors("DELETE") #TODO: maybe a PUT instead of a POST
def collaborators(request, program_id):
    pass

#/api/program/PRO_ID
@api.standardAPIErrors("GET","PATCH","DELETE")
def program(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)
    if (request.method == "GET"):
        return api.succeed(requested_program.to_dict())
    elif (request.method == "PATCH"):
        data = json.loads(request.body)
        return_data = {}

        if not requested_program.can_user_edit(request.user):
            return api.error("Not authorized.", status=401)

        if "title" in data and len(data["title"]) > 45:
            return api.error("Title length exceeds maximum characters.", status=400)

        if "publishedMessage" in data and len(data["publishedMessage"]) > 250:
            return api.error("Publish message can't exceed 250 characters")

        if "publishedMessage" in data:
            # Should it be possible to publish without an image or update the image without publishing

            try:
                image = base64toImageFile(data["imageData"], "{}.png".format(requested_program.program_id))
            except TypeError as err:
                if (err.args[0] == "Image isn't a PNG"):
                    return api.error("Image must be a PNG")
                raise
            except:
                return api.error("Invalid Image")

            requested_program.image = image

            requested_program.published_message = data["publishedMessage"]
            requested_program.last_published = datetime.datetime.now()

            return_data["lastPublished"] = requested_program.last_published.replace(microsecond=0).isoformat() + "Z"

            # Create notification for subscribers
            subscribers = requested_program.user.profile.profile_set.all()
            for subscriber in subscribers:
                Notif.objects.create(
                    target_user = subscriber.user,
                    link = "/program/" + requested_program.program_id,
                    description = "<strong>{0}</strong> just published a new program, <strong>{1}</strong>".format(
                        escape(request.user.profile.display_name), escape(requested_program.title)),
                    source_program = requested_program
                )

        valid_props = ["html", "js", "css", "title"]

        for prop in valid_props:
            if prop in data:
                setattr(requested_program, prop, data[prop])

        requested_program.save()

        return api.succeed(return_data)
    elif (request.method == "DELETE"):
        if (request.user != requested_program.user):
            return api.error("Not authorized.", status=401)

        if (requested_program.image.name != "program/nophoto.png"):
            requested_program.image.delete()

        requested_program.delete()

        return api.succeed()

#/api/programs/SORT ?limit=20&offset=0
@api.standardAPIErrors("GET")
def program_list(request, sort):
    offset = get_as_int(request.GET, "offset", 0)
    limit = get_as_int(request.GET, "limit", 20)

    if (limit > 20 or limit <= 0):
        limit = 20

    try:
        programs = get_programs(sort, offset=offset, limit=limit)
    except ValueError as e:
        return api.error(str(e))

    program_dicts = [p.to_dict(include_code=False) for p in programs]

    return api.succeed({"sort": sort, "programs": program_dicts})
