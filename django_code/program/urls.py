from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(new|[-_\w]{6})', views.program, name='program'),
]
