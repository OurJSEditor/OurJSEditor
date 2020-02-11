from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^forgot-password$',views.forgot_password, name='forgot-password'),
    url(r'^reset-password$', views.reset_password, name='reset-password'),
    url(r'^login$', views.login, name='login'), # Used for the UI for both creation and logging in
    url(r'^logout$', views.logout, name='logout'),
]
