from django.shortcuts import render, redirect
from django.http import HttpResponse

import json

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
        data = json.loads(request.body))
        user = User.objects.create_user(
            data["username"],
            data["email"],
            data["password"],
        )
        user.first_name = data["firstName"]
        user.save()

