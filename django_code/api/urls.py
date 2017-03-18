from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^users?/username_available.*', views.username_available, name='username_available'),
    url(r'^.*', views.error, name='error'),
]
