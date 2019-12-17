import re
import json

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Q

from program.models import get_programs
from ourjseditor.funcs import check_username

# Create your views here.

# username was captured by the regular expression that matched the url.
# It's passed to the function automatically.
def index(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)

        programs = get_programs("top", Q(user=user), published_only=False, limit=1000)
        program_dicts = [p.to_dict(include_code=False) for p in programs]

        user_data = {
            'user': user,
            'currentUser': request.user,
            'editing': False,
            'user_programs': json.dumps(program_dicts)
        }

        if request.user.is_authenticated:
            user_data["subscribed"] = request.user.profile.subscriptions.filter(profile_id=user.profile.profile_id).exists()

        return render(request, 'user_profile/user-profile.html', user_data)
    except User.DoesNotExist:
        return render(request, 'user_profile/does-not-exist.html', {'username': username}, status=404)

def edit(request, username):
    if (request.method == 'POST'):
       username = request.POST.get('username', '')
       display_name = request.POST.get('display_name', '')
       bio = re.sub(r'\r', '', request.POST.get('bio', ''))
       if (not check_username(username, request.user.username)):
           return HttpResponse('null', content_type="application/json", status=400)
       if (len(display_name) > 45):
           return HttpResponse('null', content_type="application/json", status=400)
       if (len(bio) > 500):
           return HttpResponse('null', content_type="application/json", status=400)
       if (display_name == ''):
           display_name = username
       request.user.username = username
       request.user.profile.display_name = display_name
       request.user.profile.bio = bio
       request.user.save()
       return redirect("/user/" + username)
    else:
        try:
            user = User.objects.select_related('profile').get(username=username)
            if (user.username == request.user.username):
                return render(request, 'user_profile/user-profile.html', {'editing': True})
            else:
                return render(request, 'user_profile/access-denied.html', {'username': username}, status=403)
        except User.DoesNotExist:
            return render(request, 'user_profile/does-not-exist.html', {'username': username}, status=404)
