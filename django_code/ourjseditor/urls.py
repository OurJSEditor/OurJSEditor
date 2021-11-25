"""ourjseditor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import re_path, include
from django.conf import settings
from django.conf.urls.static import static

from notification import api as notif_api
from user_profile import api as user_api
from account import api as account_api
from program import api as program_api
from comment import api as comment_api
from vote import api as vote_api
from program.views import new_program as new_program_view

from . import views

api_urls = [
    re_path(r'^user/', include([
        re_path(r'^new$', account_api.new_user, name='new-user-api'), # account
        re_path(r'^login$', account_api.login, name='login-api'), # account
        re_path(r'^forgot-password$', account_api.forgot_password, name='forgot-password-api'), # account
        re_path(r'^username-valid/(.+)$', user_api.username_valid, name='username-valid'),
        re_path(r'^([\w-]+)', include([
            re_path(r'^$', user_api.user, name='user-api'),
            re_path(r'^/subscribed$', user_api.subscribed, name='user-subscribed-api'),
            re_path(r'^/programs/(\w+)$', user_api.program_list, name='user-program-list-api')
        ])),
    ])),
    re_path(r'^program', include([
        re_path(r'^/new$', program_api.new_program, name="new-program-api"),
        re_path(r'^/([-\w]{6})', include([
            re_path(r'^$', program_api.program, name="program-api"),
            re_path(r'^/forks$', program_api.forks, name="program-forks-api"),
            re_path(r'^/collaborators$', program_api.collaborators, name="program-collaborators-api"),
            re_path(r'^/comments$', comment_api.program_comments, name="progrom-comments-api"),
            re_path(r'^/comment/', include([
                re_path(r'^new$', comment_api.new_comment, name="new-comment-api"),
                re_path(r'^([-\w]{10})', include([
                    re_path(r'^$', comment_api.comment, name="comment-api"),
                    re_path(r'^/comments$', comment_api.comment_comments, name="comment-comments-api"),
                ])),
            ])),
            re_path(r'^/vote$', vote_api.program_vote, name="program-vote-api"),
        ])),
        re_path(r'^s/(\w+)$', program_api.program_list, name="program-list-api"),
    ])),
    re_path(r'^comment/([-\w]{10})', include([
        re_path(r'^$', comment_api.comment, name="comment-api"),
        re_path(r'^/comments$', comment_api.comment_comments, name="comment-comments-api"),
    ])),
    re_path(r'notif', include([
        re_path(r'^/([-\w]{10})$', notif_api.notif, name="notif-api"),
        re_path(r'^s', include([
            re_path(r'^$', notif_api.notif_list, name="notif-list"),
            re_path(r'^/count$', notif_api.notif_count, name="notif-count"),
        ])),
    ])),
]

urlpatterns = [
    re_path(r'^api/', include(api_urls)),
    re_path(r'^new$', new_program_view, name="new-program"),
    re_path(r'^program', include('program.urls')),
    re_path(r'^user/', include('account.urls')),
    re_path(r'^user/', include('user_profile.urls')),
    re_path(r'^$', views.index, name='index'),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.MEDIA_URL[0] == "/" else [])
