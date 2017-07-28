from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/username_available$', views.username_available, name='username_available'),
    url(r'^user/new$', views.new_user, name='new-user-api'),
    url(r'^user/login$', views.login, name='login-api'),
    url(r'^user/(\w+)$', views.user, name='user-api'),
    url(r'^program/new$', views.new_program, name="new-program-api"),
    url(r'^program/([-\w]{6})$', views.program, name="program-api"),
]
