# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from ourjseditor import api
from models import Notif

# /notif/NOTIFIC_ID
@api.standardAPIErrors("PATCH")
@api.login_required
def notif(request, notif_id):
    notif = Notif.objects.get(notif_id=notif_id)

    if (request.method == "PATCH"):
        data = json.loads(request.body)
        read = data["isRead"] #true or false
        print(read)

        if request.user != notif.target_user:
            return api.error("Not authorized", status=401)

        if (read != True and read != False):
            return api.error("Invalid type for key \"isRead\"")

        print(notif.is_read)

        notif.is_read = read
        notif.save()

        print(notif.is_read)

        return api.succeed()
