from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def users(request):
    return error(request)

def error(request):
    return HttpResponse('null', content_type="application/json", status=400)
