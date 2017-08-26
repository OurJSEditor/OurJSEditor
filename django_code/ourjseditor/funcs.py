# A file to store miscillaneous functions that are accessed by multiple files and apps

chars = "abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
reserved_ids = ["ourjse"]
from django.contrib.auth.models import User

import random, re

def get_id():
    from program.models import Program
    from user_profile.models import Profile

    id_string = ""
    while len(id_string) < 6:
        id_string += random.choice(chars)

    if (Profile.objects.filter(profile_id=id_string).exists() or
        Program.objects.filter(program_id=id_string).exists() or
        User.objects.filter(username=id_string).exists() or
        id_string in reserved_ids):
        return get_id()
    else:
        return id_string

# Validates a username
def check_username(test_username, current_username):
    from program.models import Program
    from user_profile.models import Profile

    return (
        len(test_username) <= 45 and
        test_username != '' and
        not re.search(r"\W", test_username) and
        (test_username == current_username or not User.objects.filter(username=test_username).exists()) and
        not Program.objects.filter(program_id=test_username).exists() and
        not Profile.objects.filter(profile_id=test_username).exists()
        )
