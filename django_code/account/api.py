import json
import re
import time
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.template.loader import render_to_string

from user_profile.models import check_username
from ourjseditor import api


# /api/user/login
@api.StandardAPIErrors("POST")
def login(request):
    return api.error("Logging in is disabled", status=410)

    # data = json.loads(request.body)
    # user = auth.authenticate(
    #     username=data["username"],
    #     password=data["password"]
    # )

    # if user is None:
    #     # At this point, error should be handled by Javascript
    #     return api.error("Username or password incorrect.", status=401)

    # auth.login(request, user)
    # return api.succeed({"username": user.username})


# /api/user/forget-password
@api.StandardAPIErrors("POST")
def forgot_password(request):
    username = json.loads(request.body)["username"]
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # Other DoesNotExist errors 404, but we need this one to 400
        return api.error("No user found with matching email and username.", status=400)

    email = user.email

    timezone = int(json.loads(request.body)["timezone"])

    # Not perfect, but checks for a reasonable time value.
    if (timezone > 840 or timezone < -840):
        timezone = 0

    # Creates a time string in the form HH:MM AM|PM
    req_time = time.strftime("%I:%M %p", time.localtime(time.time() - (timezone)*60))

    token = token_generator.make_token(user)

    link = "{protocol}://{domain}/user/reset-password?{query_params}"
    link = link.format(
        protocol="https" if request.is_secure() else "http",
        domain=Site.objects.get_current().domain,
        query_params=urlencode({ "token": token, "user_id": user.profile.profile_id })
    )
    message = render_to_string("account/forgotPasswordEmail.html", {
        "link": link,
        "time": req_time,
    })

    if email != "":
        send_mail(
            subject="OurJSEditor Reset Password Request",
            from_email="email@ourjseditor.com",
            recipient_list=[email],
            message="Here's your password reset link: " + link,
            html_message=message)

    return api.succeed({"user": {"id": user.profile.profile_id}})


# /api/user/new
@api.StandardAPIErrors("POST")
def new_user(request):
    return api.error("Signing up is disabled", status=410)

    # data = json.loads(request.body)

    # username = data['username']
    # if "email" in data:
    #     email = data['email']
    # else:
    #     email = ''
    # password = data['password']
    # display_name = data['displayName']

    # if not check_username(username, ""):
    #     return api.error("Invalid username")
    # if password == "":
    #     return api.error("Password cannot be blank")
    # if display_name == "" or len(display_name) > 45:
    #     return api.error("Invalid display name")
    # if not re.match(r"^([\w.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)?$", email):
    #     return api.error("Invalid email")

    # user = User.objects.create_user(
    #     username,
    #     email,
    #     password,
    # )
    # user.profile.display_name = display_name
    # user.save()

    # auth.login(request, user)

    # return api.succeed({
    #     "id": user.profile.profile_id,
    #     "username": user.username
    # }, status=200)
