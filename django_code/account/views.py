from django.shortcuts import render
from django.http import HttpResponse

import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username').lower(),
            password=request.POST.get('password')
        )

        if user is not None:
            login(request, user)
        else:
            # Error here
            return HttpResponse("ERROR here.")
    elif request.method == 'GET':
        return HttpResponse("HTML here.")
