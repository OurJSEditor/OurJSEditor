import json

from django.contrib.auth.models import User
from django.db.models import Q

from program.models import Program, get_programs
from user_profile.models import Profile, check_username
from ourjseditor.util import get_as_int
from ourjseditor import api


# /api/user/username-valid/USERNAME
@api.StandardAPIErrors("GET")
def username_valid(request, test_username):
    return api.succeed({"usernameValid": check_username(test_username, "")})


# Return a user by username or id
def get_user(user_id, and_profile=True):
    try:
        return Profile.objects.select_related('user').get(profile_id=user_id).user
    except Profile.DoesNotExist: # If id doesn't match, we try username. If username doesn't, we throw an error caught by StandardAPIErrors
        if and_profile:
            return User.objects.select_related('profile').get(username=user_id)
        return User.objects.get(username=user_id)


# /api/user/USERNAME
@api.StandardAPIErrors("GET", "PATCH", "DELETE")
def user(request, user_id):
    requested_user = get_user(user_id)

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

            requested_user.profile.display_name = data["displayName"]

        if "bio" in data:
            if len(data["bio"]) > 500:
                return api.error("bio length exceeds maximum characters.")

            requested_user.profile.bio = data["bio"]

        if "username" in data:
            if not check_username(data["username"], requested_user.username):
                return api.error("Invalid username.")

            requested_user.username = data["username"]

        requested_user.save()

        return api.succeed()
    elif request.method == "DELETE":
        if request.user != requested_user:
            return api.error("Not authorized.", status=401)

        requested_user.delete()

        return api.succeed()


# /api/user/USERNAME/subscribed
@api.StandardAPIErrors("GET", "PATCH")
def subscribed(request, user_id):
    target_profile = get_user(user_id).profile

    is_subscribed = (
        request.user.is_authenticated and
        request.user.profile.subscriptions.filter(profile_id=target_profile.profile_id).exists()
    )

    if request.method == "GET":
        return api.succeed({"subscribed": is_subscribed})
    elif request.method == "PATCH":
        if not request.user.is_authenticated:
            return api.error("Not logged in.", status=401)

        data = json.loads(request.body)

        if not isinstance(data["subscribed"], bool):
            return api.error("Data for key 'subscribed' must be a boolean.")

        if not is_subscribed and data["subscribed"]:
            request.user.profile.subscriptions.add(target_profile)
        elif is_subscribed and not data["subscribed"]:
            request.user.profile.subscriptions.remove(target_profile)

        return api.succeed({"subscribed": data["subscribed"]})


# /api/user/USERNAME/programs/SORT
@api.StandardAPIErrors("GET", "POST")
def program_list(request, user_id, sort):
    if request.method == "POST":
        # It seems intutive that POSTing here would make a new program. However, that is not the case
        return api.error("Make a new program by posting to /api/program/new", status=405)

    requested_user = get_user(user_id, and_profile=False)

    # If the value isn't found or can't be turned into a number, these will return None
    offset = get_as_int(request.GET, "offset")
    limit = get_as_int(request.GET, "limit")

    try:
        programs = get_programs(sort, Q(user=requested_user), offset=offset, limit=limit, published_only=False)
    except ValueError as err:
        return api.error(str(err))

    program_dicts = [p.to_dict(include_code=False) for p in programs]

    return api.succeed({"sort": sort, "programs": program_dicts})
