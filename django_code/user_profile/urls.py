from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^(\w+)$', views.index, name='index'),
    re_path(r'^(\w+)/edit$', views.edit, name='edit'),
]
