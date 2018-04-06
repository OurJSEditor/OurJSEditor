from ourjseditor import api

import json

from models import Program
from views import key_func_mapping
from vote.models import vote_types

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

@api.standardAPIErrors("GET","PATCH","DELETE")
def program(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)
    if (request.method == "GET"):
        return api.succeed(requested_program.to_dict())
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

@api.standardAPIErrors("GET")
def program_list(request, sort):
    if (not sort):
        sort = "new" # Default sort. sort is actually passed in as None, so we can't use an argument default

    if (sort not in key_func_mapping):
        return api.error("Invalid sort type: \"{}\"".format(sort))

    key_func = key_func_mapping[sort]
    if (type(key_func) is unicode):
        key_func = lambda program: getattr(program, key_func_mapping[sort])

    programs = sorted(Program.objects.all(), reverse=True, key=key_func)

    program_dicts = []
    for program in programs:
        program = program.to_dict()
        del(program["css"])
        del(program["html"])
        del(program["js"])
        program_dicts.append(program)

    return api.succeed({"sort": sort, "programs": program_dicts})
