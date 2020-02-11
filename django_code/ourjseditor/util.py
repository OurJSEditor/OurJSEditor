# A file to store miscellaneous functions that are accessed by multiple files and apps

import random

from django.contrib.auth.models import User

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
RESERVED_IDS = ["ourjse"]


def get_id():
    from program.models import Program
    from user_profile.models import Profile

    id_string = ""
    while len(id_string) < 6:
        id_string += random.choice(CHARS)

    if (Profile.objects.filter(profile_id=id_string).exists() or
            Program.objects.filter(program_id=id_string).exists() or
            User.objects.filter(username=id_string).exists() or
            id_string in RESERVED_IDS):
        return get_id()

    return id_string


def get_as_int(dict_like, key, default_value):
    value = dict_like.get(key, default_value)
    try:
        value = int(value)
    except ValueError:
        value = default_value

    return value
# Validates a username


# Loosely adapted from https://github.com/encode/django-rest-framework/pull/1268
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def base64toImageFile(image_data, file_name):
    # Check if this is a base64 string
    try:
        if not isinstance(image_data, unicode):
            return None
    except NameError:  # Error on `unicode` if we're in Python 3, then we need to check if it's a str
        if not isinstance(image_data, str):
            return None

    header = None

    # Check if the base64 string is in the "data:" format
    if "data:" in image_data and ";base64," in image_data:
        # Break out the header from the base64 content
        header, image_data = image_data.split(';base64,')

    # No animated thumbnail here
    if header != "data:image/png":
        raise TypeError("Image isn't a PNG")

    # Try to decode the file. Error if it fails.
    decoded_file = base64.b64decode(image_data)

    # Verify image, adapted from https://github.com/django/django/blob/master/django/forms/fields.py#L629
    image_data_bytes = BytesIO(decoded_file)
    image = Image.open(image_data_bytes)
    image.verify()

    image = Image.open(image_data_bytes)

    if Image.MIME.get(image.format) != "image/png":
        raise TypeError("Image isn't a PNG")

    # Resize image
    image = image.resize((200, 200), Image.BICUBIC)

    image_data = BytesIO()
    image.save(image_data, format="PNG")

    return ContentFile(image_data.getvalue(), name=file_name)
