from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.

# username was captured by the regular expression that matched the url.
# It's passed to the function automatically.
def index(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)
        return render(request, 'user_profile/index.html', {'user': user})
    except User.DoesNotExist:
        return render(request, 'user_profile/doesNotExist.html', {'username': username})

def edit(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)
        if (user.username == request.user.username):
            return render(request, 'user_profile/editProfile.html')
        else:
            return render(request, 'user_profile/accessDenied.html')
    except User.DoesNotExist:
        return render(request, 'user_profile/doesNotExist.html', {'username': username})
