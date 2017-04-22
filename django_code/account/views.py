from django.shortcuts import render, redirect
from django.http import HttpResponse

import json
import re

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

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
    elif request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(request.GET.get("next") or "/")
        else:
            return HttpResponse(render(request, "account/login.html"))

def createAccount(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        display_name = request.POST.get('display_name', '')

        #Checks for valid data. This only confirms what javascript has already checked, so errors
        #don't need to be verobse. It mostly only stops people making their own fake requests.
        if (username == "" or password == "" or display_name == "" or
            re.search(r"\W", username) or len(display_name) > 45 or len(username) > 45 or
            User.objects.filter(username=username).exists() or
            not re.match(r"^([\w.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)?$", email)
            ):
            return HttpResponse('{"creationSuccess":false}', content_type="application/json", status=400)

        user = User.objects.create_user(
            username,
            email,
            password,
        )
        user.profile.display_name = display_name
        user.save()

        auth.login(request, user)

        return redirect("/user/" + username)
