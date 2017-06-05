from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/username_available', views.username_available, name='username_available'),
    url(r'^program/new', views.new_program, name="new-program-api"),
    url(r'^program/([-_\w]{6})', views.view_program, name="view-program-api"),
    url(r'^.*', views.error, name='error'),
]
