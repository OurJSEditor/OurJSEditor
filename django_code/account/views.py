from django.shortcuts import render, redirect

from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.views.decorators.csrf import ensure_csrf_cookie

from user_profile.models import Profile


# Create your views here.
@ensure_csrf_cookie
def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(request.GET.get("next") or "/user/" + request.user.username)
        else:
            return render(request, "account/login.html")


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
                return render(request, 'account/resetPassword.html', {"error": "Invalid password reset link."})

        except Profile.DoesNotExist:
            return render(request, 'account/resetPassword.html', {"error": "Invalid password reset link."})


def logout(request):
    auth.logout(request)
    return redirect("/user/login")
