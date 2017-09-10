from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(new|[-\w]{6})$', views.program, name='program'),
]
