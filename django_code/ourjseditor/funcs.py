# A file to store miscillaneous functions that are accessed by multiple files and apps

chars = "abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
reserved_ids = ["ourjse"]

import random
from django.db.utils import OperationalError

def get_id():
    from program.models import Program
    from user_profile.models import Profile

    id_string = ""
    while len(id_string) < 6:
        id_string += random.choice(chars)

    if (Profile.objects.filter(profile_id=id_string).exists()):
        return get_id()
    elif (Program.objects.filter(program_id=id_string).exists()):
        return get_id()
    elif (id_string in reserved_ids):
        return get_id()
    else:
        return id_string
