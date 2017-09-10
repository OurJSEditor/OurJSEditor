from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^user/', include([
        url(r'^username_valid/(.+)$', views.username_valid, name='username_valid'),
        url(r'^new$', views.new_user, name='new-user-api'),
        url(r'^login$', views.login, name='login-api'),
        url(r'^forgot_password$', views.forgot_password, name='forgot-password-api'),
        url(r'^(\w+)$', views.user, name='user-api'),
    ])),
    url(r'^program/new$', views.new_program, name="new-program-api"),
    url(r'^program/([-\w]{6})$', views.program, name="program-api"),
]
