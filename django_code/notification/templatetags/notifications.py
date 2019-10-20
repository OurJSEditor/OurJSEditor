import json

from django import template
from django.template.defaultfilters import escapejs

from notification.models import Notif

register = template.Library()

@register.simple_tag
def notifs_as_json(user):
    notifs = Notif.objects.filter(target_user=user).order_by("-created")
    notifs = [c.to_dict() for c in notifs]

    return escapejs(json.dumps(notifs))
