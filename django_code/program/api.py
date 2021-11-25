import json
import datetime

from django.template.defaultfilters import escape
from django.contrib.auth.models import User

from ourjseditor import api
from ourjseditor.util import base64_to_file, get_as_int

from notification.models import Notif
from user_profile.models import Profile
from .models import Program, get_programs


# /api/program/new
@api.StandardAPIErrors("POST")
@api.login_required
def new_program(request):
    data = json.loads(request.body)

    data["title"] = data["title"].strip()
    if len(data["title"]) > 45:
        return api.error("Title length exceeds maximum characters.")
    if len(data["title"]) == 0:
        return api.error("Title is blank.")

    created_program = Program.objects.create(
        user=request.user,
        title=data["title"],
        html=data["html"],
        js=data["js"],
        css=data["css"],
    )

    response = api.succeed({"id": created_program.program_id}, status=201)
    response["Location"] = "/program/" + created_program.program_id
    return response


# /api/program/PRO_ID/forks
@api.StandardAPIErrors("POST")
def forks(request, program_id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return api.error("Not logged in.", status=401)

        parent_program = Program.objects.get(program_id=program_id)

        data = json.loads(request.body)

        data["title"] = data["title"].strip()
        if len(data["title"]) > 45:
            return api.error("Title length exceeds maximum characters.")
        if len(data["title"]) == 0:
            return api.error("Title is blank.")

        created_program = Program.objects.create(
            user=request.user,
            parent=parent_program,
            title=data["title"],
            html=data["html"],
            js=data["js"],
            css=data["css"],
        )

        if parent_program.user != created_program.user:
            Notif.objects.create(
                target_user=parent_program.user,
                link="/program/" + created_program.program_id,
                description="<strong>{0}</strong> created a fork of your program, <strong>{1}</strong>".format(
                    escape(request.user.profile.display_name), escape(parent_program.title)),
            )

        response = api.succeed({"id": created_program.program_id}, status=201)
        response["Location"] = "/program/" + created_program.program_id
        return response


# /api/program/PROG_ID/collaborators
@api.StandardAPIErrors("POST", "DELETE")
def collaborators(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)

    # Any collaborator can add or remove other collaborators
    if not requested_program.can_user_edit(request.user):
        return api.error("Not authorized.", status=401)

    # Payload:
    # {user:{id:""}}
    # {user:{username:""}}
    # TODO: Allow getting a user by username *or* id?
    requested_user_identifier = json.loads(request.body)["user"]
    try:
        user = Profile.objects.get(profile_id=requested_user_identifier["id"]).user
    except KeyError:
        user = User.objects.get(username=requested_user_identifier["username"])

    if request.method == "POST":
        # Check if collaborators is already a collab
        # or is the author
        if requested_program.can_user_edit(user):
            return api.error("That user can already edit this program.")

        # Send a notification to the program owner, if it wasn't the author who did the adding
        if request.user != requested_program.user:
            Notif.objects.create(
                target_user=requested_program.user,
                link="/program/" + requested_program.program_id,
                description="<strong>{0}</strong> added <strong>{1}</strong> to the list of collaborators on your program, <strong>{2}</strong>.".format(
                    escape(request.user.profile.display_name), escape(user.profile.display_name), escape(requested_program.title)),
            )

        # Send a notification to the user who has been added
        # if (request.user != user):
        Notif.objects.create(
            target_user=user,
            link="/program/" + requested_program.program_id,
            description="<strong>{0}</strong> added you as a collaborator on the program, <strong>{1}</strong>.".format(
                escape(request.user.profile.display_name), escape(requested_program.title)),
        )

        requested_program.collaborators.add(user)
        return api.succeed({"username": user.username, "id": user.profile.profile_id})

    elif request.method == "DELETE":
        if requested_program.collaborators.filter(id=user.id).exists():
            # Send a notification to the program owner, if it wasn't the author who did the removing
            if request.user != requested_program.user:
                Notif.objects.create(
                    target_user=requested_program.user, # Program author
                    link="/program/" + requested_program.program_id,
                    description="<strong>{0}</strong> removed <strong>{1}</strong> from the list of collaborators on your program, <strong>{2}</strong>.".format(
                        escape(request.user.profile.display_name), escape(user.profile.display_name), escape(requested_program.title)),
                )

            # Send a notification to the user who was removed, unless they removed themselves
            if request.user != user:
                Notif.objects.create(
                    target_user=user,
                    link="/program/" + requested_program.program_id,
                    description="<strong>{0}</strong> removed you from the list of collaborators on the program, <strong>{1}</strong>.".format(
                        escape(request.user.profile.display_name), escape(requested_program.title)),
                )

            # Other, 3rd-party, collaborators don't get notifications

            requested_program.collaborators.remove(user)
            return api.succeed()
        return api.error("User isn't a collaborator on this program.")


# /api/program/PRO_ID
@api.StandardAPIErrors("GET", "PATCH", "DELETE")
def program(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)
    if request.method == "GET":
        return api.succeed(requested_program.to_dict())
    elif request.method == "PATCH":
        data = json.loads(request.body)
        return_data = {}

        if not requested_program.can_user_edit(request.user):
            return api.error("Not authorized.", status=401)

        if "title" in data:
            data["title"] = data["title"].strip()
            if len(data["title"]) > 45:
                return api.error("Title length exceeds maximum characters.", status=400)
            if len(data["title"]) == 0:
                return api.error("Title is blank.")

        if "publishedMessage" in data and len(data["publishedMessage"]) > 250:
            return api.error("Publish message can't exceed 250 characters")

        if "publishedMessage" in data:
            # Should it be possible to publish without an image or update the image without publishing

            try:
                image = base64_to_file(data["imageData"], "{}.png".format(requested_program.program_id))
            except TypeError as err:
                if err.args[0] == "Image isn't a PNG":
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
                    target_user=subscriber.user,
                    link="/program/" + requested_program.program_id,
                    description="<strong>{0}</strong> just published a new program, <strong>{1}</strong>".format(
                        escape(request.user.profile.display_name), escape(requested_program.title)), # Uses username of person publishing, not necessarily the program owner
                    source_program=requested_program
                )

        valid_props = ["html", "js", "css", "title"]

        for prop in valid_props:
            if prop in data:
                setattr(requested_program, prop, data[prop])

        requested_program.save()

        return api.succeed(return_data)
    elif request.method == "DELETE":
        if request.user != requested_program.user:
            return api.error("Not authorized.", status=401)

        if requested_program.image.name != "program/nophoto.png":
            requested_program.image.delete()

        requested_program.delete()

        return api.succeed()


# /api/programs/SORT ?limit=20&offset=0
@api.StandardAPIErrors("GET")
def program_list(request, sort):
    offset = get_as_int(request.GET, "offset")
    limit = get_as_int(request.GET, "limit")

    try:
        programs = get_programs(sort, offset=offset, limit=limit)
    except ValueError as err:
        return api.error(str(err))

    program_dicts = [p.to_dict(include_code=False) for p in programs]

    return api.succeed({"sort": sort, "programs": program_dicts})
