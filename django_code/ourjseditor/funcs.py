# A file to store miscillaneous functions that are accessed by multiple files and apps
# TODO: Rename this file to "util.py" and fix imports

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

def get_as_int(dict_like, key, default_value):
    value = dict_like.get(key, default_value)
    try:
        value = int(value)
    except ValueError:
        value = default_value
    
    return value
        
# TODO: Move to user_profile code
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

#Loosely adapted from https://github.com/encode/django-rest-framework/pull/1268
from django.core.files.base import ContentFile
import base64
from io import BytesIO
from PIL import Image

def base64toImageFile(imageData, file_name):
    # Check if this is a base64 string
    if isinstance(imageData, (str, unicode)):
        header = None

        # Check if the base64 string is in the "data:" format
        if "data:" in imageData and ";base64," in imageData:
            # Break out the header from the base64 content
            header, imageData = imageData.split(';base64,')

        # No animated thumbnail here
        if header != "data:image/png":
            raise TypeError("Image isn't a PNG")

        # Try to decode the file. Error if it fails.
        decoded_file = base64.b64decode(imageData)

        # Verify image, adapted from https://github.com/django/django/blob/master/django/forms/fields.py#L629
        image_data_bytes = BytesIO(decoded_file);
        image = Image.open(image_data_bytes)
        image.verify()

        image = Image.open(image_data_bytes)

        if (Image.MIME.get(image.format) != "image/png"):
            raise TypeError("Image isn't a PNG")

        # Resize image
        image = image.resize((200, 200), Image.BICUBIC)

        imageData = BytesIO()
        image.save(imageData, format="PNG")

        return ContentFile(imageData.getvalue(), name=file_name)
