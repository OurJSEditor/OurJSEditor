from django.shortcuts import render
from django.db.models import Q

from program.models import get_programs

import json

def index(request):
    top_programs = get_programs("top", limit=3)
    programs = {
        "popular": [p.to_dict(include_code=False) for p in top_programs],
    }
    
    if (request.user.is_authenticated):
        recently_created = get_programs("new", Q(user=request.user), published_only=False, limit=3)
        subscriptions = get_programs("new", Q(user__profile__in=request.user.profile.subscriptions.all()), limit=4)
        
        programs["recent"] = [p.to_dict(include_code=False) for p in recently_created]
        programs["subscriptions"] = [p.to_dict(include_code=False) for p in subscriptions]
    
    return render(request, 'ourjseditor/index.html', {
        "programs": json.dumps(programs)
    })
