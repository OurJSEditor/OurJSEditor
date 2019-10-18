# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django import db

import json

def error(text, data={}, status=400):
    data["success"] = False
    data["error"] = text
    return HttpResponse(
        json.dumps(data),
        status=status,
        content_type="application/json"
    )

def succeed(data={}, status=200):
    data["success"] = True
    return HttpResponse(
        json.dumps(data),
        status=status,
        content_type="application/json"
    )

#Decorator for when some login is required
def login_required(func):
    def new_func(request, *args):
        if (request.user.is_authenticated):
            return func(request, *args)
        else:
            return error("Not logged in.", status=401)
    return new_func

#Decorator for most standard try...except blocks.
#Takes a list of accepted methods, (e.g. "POST", "GET", etc.) and errors if the method isn't allowed
class standardAPIErrors(object):
    def __init__(self, *args):
        self.accepted_methods = args

    def __call__(self, func):
        def new_func(request, *args):
            if (request.method in self.accepted_methods):
                try:
                    return func(request, *args)
                #Most often this is when JSON.loads fails, but also catches other weird cases
                except ValueError:
                    if request.method not in ["POST","PATCH"]:
                        raise
                    return error("Missing or malformed JSON.")
                #JSON errors
                except KeyError as err:
                    if request.method not in ["POST", "PATCH"]:
                        raise
                    return error("Missing data for {}.".format(str(err)))
                #Random stuff, like calling len() on a number or ["hi"] on something that's not a dict
                except TypeError as err:
                    return error("TypeError", data={"internalError": str(err)})
                #When we try to .get() something and it doesn't exist
                except ObjectDoesNotExist:
                    return error("The requested object could not be found (because it doesn't exist).", status=404)
                #db.Error if the db rejects what we try to include
                except db.Error:
                    return error("Invalid data. (This should have been caught earlier. Can you report this?)")
            else:
                return error("Method '{}' not allowed.".format(request.method), status=405)
        return new_func
