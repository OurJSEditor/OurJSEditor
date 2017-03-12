from django.shortcuts import render
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
            return HttpResponse("\"Success\"", content_type="application/json")
        else:
            # Error here
            return HttpResponse("\"Login failed\"", content_type="application/json")
    elif request.method == 'GET':
        return HttpResponse(render(request, "account/login.html"))
