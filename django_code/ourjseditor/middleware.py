import re

from django import http
from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin

from . import api


# Adapted from https://github.com/dghubble/django-unslashed/blob/master/unslashed/middleware.py
class RemoveSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if getattr(settings, 'APPEND_SLASH') and getattr(settings, 'REMOVE_SLASH'):
            raise ImproperlyConfigured("APPEND_SLASH and REMOVE_SLASH may not both be True.")

        old_url = request.path_info # path_info only includes path, query information
        if getattr(settings, 'REMOVE_SLASH', False) and old_url[-1] == "/":
            urlconf = getattr(request, 'urlconf', None)

            new_url = old_url[:-1]

            # If the url with a / would 404 and without a slash wouldn't
            if (not urlresolvers.is_valid_path(old_url, urlconf)) and urlresolvers.is_valid_path(new_url, urlconf):
                if settings.DEBUG and request.method == 'POST':
                    if old_url.startswith("/api/"):
                        return api.error("You made a POST request to a URL ending with a slash. Please repeat your request without the slash.")

                    raise RuntimeError((""
                        "You called this URL via POST, but the URL ends in a "
                        "slash and you have REMOVE_SLASH set. Django can't "
                        "redirect to the non-slash URL while maintaining POST "
                        "data. Change your form to point to %s (without a "
                        "trailing slash), or set REMOVE_SLASH=False in your "
                        "Django settings.") % (new_url))

                # The ? and everything after
                query_data = re.match(r'^[^?]*(\?.*)?$', request.build_absolute_uri()).group(1) or ""

                return http.HttpResponsePermanentRedirect(new_url + query_data)
