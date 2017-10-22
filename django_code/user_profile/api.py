from django.contrib.auth.models import User

import json

from program.models import Program
from user_profile.models import Profile
from ourjseditor.funcs import check_username
from ourjseditor import api

@api.standardAPIErrors("GET")
def username_valid(request, username):
    return api.succeed({ "usernameValid": check_username(username, "") })

@api.standardAPIErrors("GET","PATCH","DELETE")
def user(request, id):
    try:
        requested_user = Profile.objects.select_related('user').get(profile_id=id).user
    except Profile.DoesNotExist:
        #If id doesn't match, we try username. If username doesn't, we throw an error caught by standardAPIErrors
        requested_user = User.objects.select_related('profile').get(username=id)

    if request.method == "GET":
        user_data = {
            "username": requested_user.username,
            "id": requested_user.profile.profile_id,
            "displayName": requested_user.profile.display_name,
            "bio": requested_user.profile.bio,
            "programs": list(Program.objects.filter(user=requested_user).values_list("program_id", flat=True))
        }
        return api.succeed(user_data)
    elif request.method == "PATCH":
        data = json.loads(request.body)

        if request.user != requested_user:
            return api.error("Not authorized.", status=401)

        if "displayName" in data:
            if len(data["displayName"]) > 45:
                return api.error("displayName length exceeds maximum characters.")
            else:
                requested_user.profile.display_name = data["displayName"]

        if "bio" in data:
            if len(data["bio"]) > 500:
                return api.error("bio length exceeds maximum characters.")
            else:
                requested_user.profile.bio = data["bio"]

        if "username" in data:
            if  (not check_username(data["username"], requested_user.username)):
                return api.error("Invalid username.")
            else:
                requested_user.username = data["username"]

        requested_user.save()

        return api.succeed()
    elif (request.method == "DELETE"):
        if request.user != requested_user:
            return api.error("Not authorized.", status=401)

        requested_user.delete()

        return api.succeed()
