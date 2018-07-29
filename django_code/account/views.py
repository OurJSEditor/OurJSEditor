from django.shortcuts import render, redirect
from django.http import HttpResponse

import json, re

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator as token_generator

from ourjseditor.funcs import check_username
from user_profile.models import Profile

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
        display_name = request.POST.get('displayName', '')

        #Checks for valid data. This only confirms what javascript has already checked, so errors
        #don't need to be verobse. It mostly only stops people making their own fake requests.
        if (password == "" or display_name == "" or len(display_name) > 45 or
            not check_username(username, "") or
            not re.match(r"^([\w.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)?$", email)
            ):
            return render(request, "account/login.html", {"error": "Your request seems wrong for some reason. What did you do?"})

        user = User.objects.create_user(
            username,
            email,
            password,
        )
        user.profile.display_name = display_name
        user.save()

        auth.login(request, user)

        return redirect("/user/" + username)

def forgot_password(request):
    return render(request, 'account/forgotPassword.html')

def reset_password(request):
    if (request.method == "GET"):
        return render(request, 'account/resetPassword.html', request.GET.dict())
    elif (request.method == "POST"):
        profile_id = request.POST.get("user_id","")
        token = request.POST.get("token","")

        try:
            user = Profile.objects.get(profile_id=profile_id).user
            if (token_generator.check_token(user, token)):
                user.set_password(request.POST.get("password"))
                user.save()
                auth.login(request, user)
                return redirect("/user/" + user.username)
            else:
                return render(request, 'account/resetPassword.html', {"error": "Invalid token or user."})

        except Profile.DoesNotExist:
            return render(request, 'account/resetPassword.html', {"error": "Invalid user."})

def logout(request):
    auth.logout(request);
    return redirect("/");
