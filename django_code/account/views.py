from django.shortcuts import render, redirect
from django.http import HttpResponse

import json, re

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from ourjseditor.funcs import check_username

# Create your views here.

def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(request.GET.get("next") or "/user/" + request.user.username)
        else:
            return render(request, "account/login.html")

def new_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        display_name = request.POST.get('display_name', '')

        #Checks for valid data. This only confirms what javascript has already checked, so errors
        #don't need to be verobse. It mostly only stops people making their own fake requests.
        if (password == "" or display_name == "" or len(display_name) > 45 or
            not check_username(username, "") or
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
