import json

from packages.bin.auth import Auth
from django.http import HttpResponse
from django.db.models.query_utils import Q


#===============================================================================
# HR - STAFF PROFILE
#===============================================================================
def Profile(request, qs=""):
    
    from packages.hr.hr_personnel.models import Basic
    
    s = Auth().isAuth(request)
    if not s:
        return Auth.routeLogin
    
    qs = request.GET.get('qac')
    
    data = []
    profiles = Basic.objects.filter(Q(firstname__icontains=qs) | Q(lastname__icontains=qs))[:25]
    for profile in profiles:
        data.append({'id': profile.id, 'name': "%s %s" % (profile.firstname, profile.lastname)})
    
    data = json.dumps(data)
    return HttpResponse(data)