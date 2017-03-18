from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

# Create your views here.

def username_available(request):
    username = request.GET.get("username", "")
    if (username == ""):
        return error(request)
    try:
        user = User.objects.get(username=username)
        return HttpResponse('{"username_available":false}', content_type="application/json", status=200)
    except User.DoesNotExist:
        return HttpResponse('{"username_available":true}', content_type="application/json", status=200)

def error(request):
    return HttpResponse('null', content_type="application/json", status=400)
