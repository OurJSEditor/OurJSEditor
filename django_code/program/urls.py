from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'new', views.new_program, name='new_program'),
    url(r'^(.*)', views.program, name='program'),
]
