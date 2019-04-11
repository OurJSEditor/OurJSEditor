"""ourjseditor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin

from . import views

from notification import api as notif_api
from user_profile import api as user_api
from account import api as account_api
from program import api as program_api
from comment import api as comment_api
from vote import api as vote_api

from program.views import new_program as new_program_view

api_urls = [
    url(r'^user/', include([
        url(r'^new$', account_api.new_user, name='new-user-api'), #account
        url(r'^login$', account_api.login, name='login-api'), #account
        url(r'^forgot-password$', account_api.forgot_password, name='forgot-password-api'), #account
        url(r'^username-valid/(.+)$', user_api.username_valid, name='username-valid'),
        url(r'^([\w-]+)', include([
            url(r'^$', user_api.user, name='user-api'),
            url(r'^/subscribed$', user_api.subscribed, name='user-subscribed-api')
        ])),
    ])),
    url(r'^program', include([
        url(r'^/new$', program_api.new_program, name="new-program-api"),
        url(r'^/([-\w]{6})', include([
            url(r'^$', program_api.program, name="program-api"),
            url(r'^/forks$', program_api.forks, name="program-forks-api"),
            url(r'^/comments$', comment_api.program_comments, name="progrom-comments-api"),
            url(r'^/comment/', include([
                url(r'^new$', comment_api.new_comment, name="new-comment-api"),
                url(r'^([-\w]{10})', include([
                    url(r'^$', comment_api.comment, name="comment-api"),
                    url(r'^/comments$', comment_api.comment_comments, name="comment-comments-api"),
                ])),
            ])),
            url(r'^/vote$', vote_api.program_vote, name="program-vote-api"),
        ])),
        url(r'^(?:s|s/(\w+))$', program_api.program_list, name="program-list-api"),
    ])),
    url(r'^comment/([-\w]{10})', include([
        url(r'^$', comment_api.comment, name="comment-api"),
        url(r'^/comments$', comment_api.comment_comments, name="comment-comments-api"),
    ])),
    url(r'notif', include([
        url(r'^/([-\w]{10})$', notif_api.notif, name="notif-api"),
        url(r'^s', include([
            url(r'^$', notif_api.notif_list, name="notif-list"),
            url(r'^/count$', notif_api.notif_count, name="notif-count"),
        ])),
    ])),
]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urls)),
    url(r'^new$', new_program_view, name="new-program"),
    url(r'^program', include('program.urls')),
    url(r'^user/', include('account.urls')),
    url(r'^user/', include('user_profile.urls')),
    url(r'^$', views.index, name='index'),
]
