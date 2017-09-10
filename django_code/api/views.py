from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from django import db
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.template.loader import render_to_string

import json
import re
import urllib
import time

from program.models import Program
from user_profile.models import Profile
from ourjseditor.funcs import check_username

# Create your views here.

def username_valid(request, username):
    valid = "false"
    if (check_username(username, "")):
        valid = "true"

    return HttpResponse('{"usernameValid":%s}' % valid, content_type="application/json", status=200)


def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = auth.authenticate(
            username=data["username"],
            password=data["password"]
        )

        if user is not None:
            auth.login(request, user)
            return HttpResponse('{"loginSuccess":true,"username":"' + user.username + '"}', content_type="application/json")
        else:
            # At this point, error should be handled by Javascript
            return HttpResponse('{"loginSuccess":false}', content_type="application/json")
    else:
        return HttpResponse("The method " + request.method + " is not allowed for the requested URL.", status=405)

def forgot_password(request):
    if request.method == 'POST':
        try:
            email = json.loads(request.body)["email"]
            username = json.loads(request.body)["username"]
            user = User.objects.get(email=email,username=username)

            timezone = int(json.loads(request.body)["timezone"])

            #Not perfect, but checks for a reasonable time value.
            if (timezone > 840 or timezone < -840):
                timezone = 0

            # Creates a time string in the form HH:MM AM|PM
            req_time = time.strftime("%I:%M %p", time.localtime(time.time() - (timezone)*60))

            token = token_generator.make_token(user)

            link = "{protocol}://{domain}/user/reset-password?{query_params}"
            link = link.format(
                protocol="https" if request.is_secure() else "http",
                domain=Site.objects.get_current().domain,
                query_params=urllib.urlencode(dict(token=token,user_id=user.profile.profile_id))
            )
            message = render_to_string("account/forgotPasswordEmail.html", {
                "link": link,
                "time": req_time,
            })

            send_mail(
                subject="OurJSEditor Reset Password Request",
                from_email="email@ourjseditor.com",
                recipient_list=[email],
                message="Here's your password reset link: " + link,
                html_message=message)

            return HttpResponse('{"resetRequestSuccess":true,"userId":"%s"}' % user.profile.profile_id, content_type="application/json")
        except User.DoesNotExist:
            return HttpResponse('{"resetRequestSuccess":false,"error":"No user found with matching email and username."}', content_type="application/json", status=400)
        except KeyError as err:
            return HttpResponse('{"resetRequestSuccess":false, "error":"Missing data for %s."}' % str(err), content_type="application/json", status=400)
        except ValueError:
            return HttpResponse('{"resetRequestSuccess":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)

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
                author_id = requested_program.user.profile.profile_id,
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

                if "title" in data and len(data["title"]) > 45:
                    return HttpResponse('{"success":false, "error":"Title length exceeds maximum characters."}', content_type="application/json", status=400)

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

def user(request, id):
    try:
        requested_user = Profile.objects.select_related('user').get(profile_id=id).user
    except Profile.DoesNotExist:
        try:
            requested_user = User.objects.select_related('profile').get(username=id)
        except User.DoesNotExist:
            return HttpResponse("No user with matching username or id.", status=404)

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
                    return HttpResponse('{"creationSuccess":false, "error":"display_name length exceeds maximum characters."}', content_type="application/json", status=400)
                else:
                    requested_user.profile.display_name = data["display_name"]

            if "bio" in data:
                if len(data["bio"]) > 500:
                    return HttpResponse('{"creationSuccess":false, "error":"bio length exceeds maximum characters."}', content_type="application/json", status=400)
                else:
                    requested_user.profile.bio = data["bio"]

            if "username" in data:
                if  (check_username(data["username"], requested_user.username)):
                    return HttpResponse('{"creationSuccess":false, "error":"Invalid username."}', content_type="application/json", status=400)
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
        return HttpResponse("The method " + request.method + " is not allowed for the requested URL.", status=405)

def new_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data['username']
            email = data['email']
            password = data['password']
            display_name = data['display_name']

            if (not check_username(username, "")):
                return HttpResponse('{"creationSuccess":false,"error":"Invalid username"}', content_type="application/json", status=400)
            if (password == ""):
                return HttpResponse('{"creationSuccess":false,"error":"Password cannot be blank"}', content_type="application/json", status=400)
            if (display_name == "" or len(display_name) > 45):
                return HttpResponse('{"creationSuccess":false,"error":"Invalid display name"}', content_type="application/json", status=400)
            if (not re.match(r"^([\w.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)?$", email)):
                return HttpResponse('{"creationSuccess":false,"error":"Invalid email"}', content_type="application/json", status=400)

            user = User.objects.create_user(
                username,
                email,
                password,
            )
            user.profile.display_name = display_name
            user.save()

            auth.login(request, user)

            response = HttpResponse('{"creationSuccess":true}', content_type="application/json", status=201)
            response["Location"] = "/user/" + user.username
            return response
        except KeyError as err:
            return HttpResponse('{"creationSuccess":false, "error":"Missing data for %s."}' % str(err), content_type="application/json", status=400)
        except ValueError:
            return HttpResponse('{"success":false,"error":"Missing or malformed JSON."}', content_type="application/json", status=400)


def error(request):
    return HttpResponse('null', content_type="application/json", status=400)
