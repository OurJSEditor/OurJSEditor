from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.template.loader import render_to_string

import json
import re
import urllib
import time

from ourjseditor.funcs import check_username

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
