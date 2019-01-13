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
            "programs": list(Program.objects.filter(user=requested_user).values_list("program_id", flat=True)),
            "joined": requested_user.date_joined.replace(microsecond=0).isoformat() + "Z"
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

@api.standardAPIErrors("GET", "PATCH")
def subscribed(request, id):
    try:
        target_profile = Profile.objects.get(profile_id=id)
    except Profile.DoesNotExist:
        # If id doesn't match, we try username. If username doesn't, we throw an error caught by standardAPIErrors
        target_profile = User.objects.select_related('profile').get(username=id).profile

    is_subscribed = bool(request.user.is_authenticated and
        request.user.profile.subscriptions.filter(profile_id=target_profile.profile_id))

    if request.method == "GET":
        return api.succeed({ "subscribed": is_subscribed })
    elif request.method == "PATCH":
        if not request.user.is_authenticated:
            return api.error("Not logged in.", status=401)

        data = json.loads(request.body)
        subscribed = data["subscribed"]

        if type(subscribed) is not bool:
            return api.error("Data for key 'subscribed' must be a boolean.")

        if not is_subscribed and data["subscribed"]:
            request.user.profile.subscriptions.add(target_profile)
        elif is_subscribed and not data["subscribed"]:
            request.user.profile.subscriptions.remove(target_profile)

        return api.succeed({ "subscribed": data["subscribed"] })
