
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(\w+)$', views.index, name='index'),
    url(r'^(\w+)/edit$', views.edit, name='edit'),
]
