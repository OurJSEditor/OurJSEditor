from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'ourjseditor/index.html', {
        'logged_in': request.user.is_authenticated,
        'username': request.user.username
    })
