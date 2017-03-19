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
        #return HttpResponse(request.body)

        if user is not None:
            auth.login(request, user)
            return HttpResponse('{"loginSuccess":true}', content_type="application/json")
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
        data = json.loads(request.body)

        username = data["username"]
        email = data["email"]
        password = data["password"]
        firstName = data["firstName"]

        #Checks for valid data. This only confirms what javascript has already checked, so errors
        #don't need to be verobse. It mostly only stops people making their own fake requests.
        if (username == "" or email == "" or password == "" or firstName == "" or
            re.match(r"[^A-Za-z0-9_]", username) or
            User.objects.filter(username=username).exists() or
            not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
            ):
            return HttpResponse('{"creationSuccess":false}', content_type="application/json", status=400)

        user = User.objects.create_user(
            username,
            email,
            password,
        )
        user.first_name = data["firstName"]
        user.save()

        auth.login(request, user)

        response = HttpResponse('{"creationSuccess":true}', content_type="application/json", status=201)
        response["Location"] = "/user/" + username
        return response
