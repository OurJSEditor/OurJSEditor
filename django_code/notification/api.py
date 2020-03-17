from __future__ import unicode_literals

import json

from ourjseditor import api
from .models import Notif


# /notif/NOTIFIC_ID
@api.StandardAPIErrors("PATCH")
@api.login_required
def notif(request, notif_id):
    requested_notif = Notif.objects.get(notif_id=notif_id)

    if request.method == "PATCH":
        data = json.loads(request.body)
        read = data["isRead"] # true or false

        if request.user != requested_notif.target_user:
            return api.error("Not authorized", status=401)

        if not isinstance(read, bool):
            return api.error("Invalid type for key \"isRead\"")

        requested_notif.is_read = read
        requested_notif.save()

        return api.succeed()


# /notifs
@api.StandardAPIErrors("GET")
@api.login_required
def notif_list(request):
    notifs = Notif.objects.filter(target_user=request.user).order_by("-created")
    notifs = [n.to_dict() for n in notifs]

    return api.succeed({"notifs": notifs})


# /notifs/count
@api.StandardAPIErrors("GET")
@api.login_required
def notif_count(request):
    return api.succeed({
        "notifCount": Notif.objects.filter(target_user=request.user, is_read=False).count()
    })
