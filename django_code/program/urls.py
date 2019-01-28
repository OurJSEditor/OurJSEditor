from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^/(new|[-\w]{6})$', views.program, name='program'),
    url(r'^/([-\w]{6})\.(js|html|css)$', views.program_file, name='program-file'),
    url(r'^/([-\w]{6})/fullscreen$', views.fullscreen, name='program-fullscreen'),
    url(r'^(?:s|s/(\w+))$', views.program_list, name='program-list')
]
