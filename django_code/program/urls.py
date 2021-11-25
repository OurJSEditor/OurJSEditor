from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^/(unsaved|[-\w]{6})$', views.program, name='program'),
    re_path(r'^/([-\w]{6})\.(js|html|css)$', views.program_file, name='program-file'),
    re_path(r'^/([-\w]{6})/fullscreen$', views.fullscreen, name='program-fullscreen'),
    re_path(r'^(?:s|s/(\w+))$', views.program_list, name='program-list')
]
