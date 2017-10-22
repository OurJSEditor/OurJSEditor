from ourjseditor import api

import json

from models import Program

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

    response = api.succeed({"id": program.program_id}, status=201)
    response["Location"] = "/program/" + program.program_id
    return response

# @api.standardAPIErrors("GET","PATCH","DELETE")
def program(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)
    if (request.method == "GET"):
        program_data = {
            "author": { "id": requested_program.user.profile.profile_id },
            "created": requested_program.created.replace(microsecond=0).isoformat() + "Z",
            "id": requested_program.program_id,
            "title": requested_program.title,
            "css": requested_program.css,
            "js": requested_program.js,
            "html": requested_program.html
        }
        return api.succeed(program_data)
    elif (request.method == "PATCH"):
        data = json.loads(request.body)

        if request.user != requested_program.user:
            return api.error("Not authorized.", status=401)

        valid_props = ["html", "js", "css", "title"]

        if "title" in data and len(data["title"]) > 45:
            return api.error("Title length exceeds maximum characters.", status=400)

        for prop in valid_props:
            if prop in data:
                setattr(requested_program, prop, data[prop])

        requested_program.save()

        return api.succeed({})
    elif (request.method == "DELETE"):
        if request.user != requested_program.user:
            return api.error("Not authorized.", status=401)

        requested_program.delete()

        return api.succeed({})
