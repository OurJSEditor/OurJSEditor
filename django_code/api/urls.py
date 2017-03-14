from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^users?.*', views.users, name='users'),
    url(r'^.*', views.error, name='error'),
]
