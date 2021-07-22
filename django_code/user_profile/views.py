import re
import json

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Q

from program.models import get_programs, PROGRAMS_PER_PAGE
from user_profile.models import check_username


# username was captured by the regular expression that matched the url.
# It's passed to the function automatically.
def index(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)

        list_options = {
            'perPage': PROGRAMS_PER_PAGE,
            'sort': 'new' if user == request.user else 'top' # If you're looking at your own profile, show new programs
        }

        programs = get_programs(list_options['sort'], Q(user=user), published_only=False, initial_load=True)
        program_dicts = [p.to_dict(include_code=False) for p in programs]

        list_options["initialPrograms"] = program_dicts
        user_data = {
            'user': user,
            'currentUser': request.user,
            'editing': False,
            'listOptions': json.dumps(list_options)
        }

        if request.user.is_authenticated:
            user_data["subscribed"] = request.user.profile.subscriptions.filter(profile_id=user.profile.profile_id).exists()

        return render(request, 'user_profile/user-profile.html', user_data)
    except User.DoesNotExist:
        return render(request, 'user_profile/does-not-exist.html', {'username': username}, status=404)


def edit(request, username):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        display_name = request.POST.get('display_name', '')
        bio = re.sub(r'\r', '', request.POST.get('bio', ''))
        if not check_username(username, request.user.username):
            return HttpResponse('null', content_type="application/json", status=400)
        if len(display_name) > 45:
            return HttpResponse('null', content_type="application/json", status=400)
        if len(bio) > 500:
            return HttpResponse('null', content_type="application/json", status=400)
        if display_name == '':
            display_name = username
        request.user.username = username
        request.user.profile.display_name = display_name
        request.user.profile.bio = bio
        request.user.save()
        return redirect("/user/" + username)
    else:
        try:
            user = User.objects.select_related('profile').get(username=username)
            if user.username == request.user.username:
                return render(request, 'user_profile/user-profile.html', {'editing': True})

            return render(request, 'user_profile/access-denied.html', {'username': username}, status=403)
        except User.DoesNotExist:
            return render(request, 'user_profile/does-not-exist.html', {'username': username}, status=404)
