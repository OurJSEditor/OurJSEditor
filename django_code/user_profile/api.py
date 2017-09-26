from django.http import HttpResponse
from django.contrib.auth.models import User

import json

from program.models import Program
from user_profile.models import Profile
from ourjseditor.funcs import check_username

def username_valid(request, username):
    valid = "false"
    if (check_username(username, "")):
        valid = "true"

    return HttpResponse('{"usernameValid":%s}' % valid, content_type="application/json", status=200)

def user(request, id):
    try:
        requested_user = Profile.objects.select_related('user').get(profile_id=id).user
    except Profile.DoesNotExist:
        try:
            requested_user = User.objects.select_related('profile').get(username=id)
        except User.DoesNotExist:
            return HttpResponse('{"success":false,"error":"No user with matching username or id."}', status=404)

    if request.method == "GET":
        user_dict = dict(
            username = requested_user.username,
            id = requested_user.profile.profile_id,
            displayName = requested_user.profile.display_name,
            bio = requested_user.profile.bio,
            programs = list(Program.objects.filter(user=requested_user).values_list("program_id", flat=True))
        )
        return HttpResponse(json.dumps(user_dict), content_type="application/json", status=200)
    elif request.method == "PATCH":
        try:
            data = json.loads(request.body)

            if request.user != requested_user:
                return HttpResponse('{"success":false,"error":"Not authorized."}', content_type="application/json", status=403)

            if "display_name" in data:
                if len(data["display_name"]) > 45:
                    return HttpResponse('{"success":false, "error":"display_name length exceeds maximum characters."}', content_type="application/json", status=400)
                else:
                    requested_user.profile.display_name = data["display_name"]

            if "bio" in data:
                if len(data["bio"]) > 500:
                    return HttpResponse('{"success":false, "error":"bio length exceeds maximum characters."}', content_type="application/json", status=400)
                else:
                    requested_user.profile.bio = data["bio"]

            if "username" in data:
                if  (check_username(data["username"], requested_user.username)):
                    return HttpResponse('{"success":false, "error":"Invalid username."}', content_type="application/json", status=400)
                else:
                    requested_user.username = data["username"]

            requested_user.save()

            return HttpResponse('', status=204)
        except ValueError:
            return HttpResponse('{"success":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)
    elif (request.method == "DELETE"):
        if request.user != requested_user:
            return HttpResponse('{"success":false,"error":"Not authorized."}', content_type="application/json", status=403)

        requested_user.delete()

        return HttpResponse('', status=204)
    else:
        return HttpResponse('{"success":false,"error":"The method ' + request.method + ' is not allowed for the requested URL."}', content_type="application/json", status=405)
