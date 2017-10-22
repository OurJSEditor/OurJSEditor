import re
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

from program.models import Program
from ourjseditor.funcs import check_username

# Create your views here.

# username was captured by the regular expression that matched the url.
# It's passed to the function automatically.
def index(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)
        return render(request, 'user_profile/user_profile.html', {
            'user': user,
            'currentUser': request.user,
            'editing': False,
            'user_programs': Program.objects.filter(user=user).order_by("-created")
        })
    except User.DoesNotExist:
        return render(request, 'user_profile/doesNotExist.html', {'username': username}, status=404)

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
       request.user.username = username;
       request.user.profile.display_name = display_name;
       request.user.profile.bio = bio;
       request.user.save()
       return redirect("/user/" + username)
    else:
        try:
            user = User.objects.select_related('profile').get(username=username)
            if (user.username == request.user.username):
                return render(request, 'user_profile/user_profile.html', {'editing': True})
            else:
                return render(request, 'user_profile/accessDenied.html', {'username': username}, status=403)
        except User.DoesNotExist:
            return render(request, 'user_profile/doesNotExist.html', {'username': username}, status=404)
