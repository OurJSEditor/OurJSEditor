from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^forgot_password$',views.forgot_password, name='forgot-password'),
    url(r'^reset_password$', views.reset_password, name='reset-password'),
    url(r'^login$', views.login, name='login'), #Used for the UI for both creation and logging in
    url(r'^new$', views.new_user, name='new-user'), #Used by POST for creation
]
