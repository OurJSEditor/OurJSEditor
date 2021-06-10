from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^forgot-password$',views.forgot_password, name='forgot-password'),
    re_path(r'^reset-password$', views.reset_password, name='reset-password'),
    re_path(r'^login$', views.login, name='login'), # Used for the UI for both creation and logging in
    re_path(r'^logout$', views.logout, name='logout'),
]
