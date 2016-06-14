import json
import urllib

from packages.bin.auth import Auth

from django.http import HttpResponse
from django.db.models.query_utils import Q

#===============================================================================
# HR - STAFF PROFILE
#===============================================================================
def User(request, qs=""):

    from packages.system.models import Users
    from packages.hr.hr_personnel.models import Basic

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    data = []
    c_list = Users.pp.filter(Q(username__icontains=qs) | Q(profile__firstname__icontains=qs) | Q(profile__lastname__icontains=qs))[:25]
    for x in c_list:
        data.append({'id':x.id, 'name':"%s [%s %s]"%(x.username, x.profile.firstname, x.profile.lastname)})

    data = json.dumps(data)
    return HttpResponse(data)


def Profile(request):
    
    from packages.hr.hr_personnel.models import Basic
    
    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin
    
    qs = request.GET.get('qac') or ""
    
    data = []
    profiles = Basic.pp.filter(Q(firstname__icontains=qs) | Q(lastname__icontains=qs))[:25]
    for profile in profiles:
        data.append(profile.get_autocomplete())
    
    data = json.dumps(data)
    return HttpResponse(data)


def location(request):

    from django.db.models import Q
    from packages.hr.hr_organization.models import Location

    qs = request.GET.get('qac') or ""

    data = []
    obj = Location.objects.filter(Q(name__icontains=qs) | Q(city__icontains=qs) | Q(state__icontains=qs) |
    Q(country__icontains=qs))[:25]
    for val in obj:
        data.append({'id': val.pk, 'name': "%s" % (val.name[:60])})

    data = json.dumps(data)

    return HttpResponse(data)


def InventoryItem(request, qs=""):

    from packages.bin.lib import drop_down
    from packages.hr.hr_organization.models import Organization
    from packages.inventory.models import Item

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    # split qs into 2 halves of "::" separator
    if qs is not None:
        qs = qs.split("::")[0]

    else:
        qs = " "

    organization = Organization.pp.get(profile__id=request.session['auth_idp'])

    try:
        qm = request.GET.get('mode')
    except ValueError:
        qm = None

    data = []
    obj = Item.pp.filter(Q(name__icontains=qs) | Q(barcode__icontains=qs))[:25]

    if qm is None:
        for val in obj:
            data.append({'id':val.id, 'name':"%s"%(val.name)})

    elif qm == 'all':
        # val = Item.pp.filter(Q(name__icontains=qs) | Q(barcode__iexact=qs))[0]
        if qs != "":
            val = Item.pp.filter(barcode__iexact=qs)[0]
        else:
            return HttpResponse(data)

        # stock = val.item_stock.filter(location=organization.location)[0].quantity

        #uom_dict = [{1.0: 'Single'}]
        uom_dict = []
        uoms = val.uom_item.all().order_by('uom_dict__id')
        for uom in uoms:
            try:
                stock = uom.item_stock_uom.all()[0].quantity
            except IndexError:
                stock = 0

            if stock > 0:
                uom_dict.append({str(uom.id): str(uom.uom_dict.name) + ' of ' + str(uom.quantity)})

        uom_dict_dd = drop_down(uom_dict, default='single', id='item_uom')

        # iterate through all UOM indexes
        for uom_obj in val.uom_item.all().order_by('uom_dict__id'):
            try:
                stock = uom_obj.item_stock_uom.all()[0].quantity
                if stock > 0:
                    data.append({'id':val.id, 'name':"%s"%(val.name), 'barcode':"%s"%(val.barcode),
                    'stock':"%s"%(stock), 'price1':"%s"%(uom_obj.price1), 'price2':"%s"%(uom_obj.price2),
                    'price3':"%s"%(uom_obj.price3), 'uom':"%s"%(uom_dict_dd)})
            except IndexError:
                pass

    else:
        for val in obj:
            try:
                stock = val.item_stock.filter(location=organization.location)[0].quantity
            except IndexError:
                stock = 0

            if stock > 0:
                data.append("%s::%s"%(val.barcode, val.name))

    data = json.dumps(data)
    return HttpResponse(data)


def CRM_Profile(request, qs=""):

    from packages.bin.lib import drop_down
    from packages.crm.crm_index.models import CIM

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    # split qs into 2 halves of "::" separator
    qs = qs.split("::")[0]

    try:
        qm = request.GET.get('mode')
    except ValueError:
        qm = None

    data = []
    obj = CIM.pp.filter(Q(name__icontains=qs) | Q(phone__icontains=qs) | Q(email__icontains=qs))[:25]

    if qm is None:
        for val in obj:
            data.append({'id':val.id, 'name':"%s"%(val.name)})

    else:
        for val in obj:
            data.append("%s::%s"%(val.id, val.name))

    data = json.dumps(data)
    return HttpResponse(data)


def Privilege_Manifest(request, qs=""):

    from packages.system.models import PrivilegeManifest

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    data = []
    c_list = PrivilegeManifest.objects.filter(Q(module__name__icontains=qs) | Q(name__icontains=qs))[:25]
    for x in c_list:
        data.append({'id': x.id, 'name': "%s/%s" % (x.module.name, x.name)})

    data = json.dumps(data)
    return HttpResponse(data)


def System_UserClass(request):

    from packages.system.models import UserClass

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    data = []
    c_list = UserClass.objects.filter(Q(module__name__icontains=qs) | Q(name__icontains=qs))[:25]
    for x in c_list:
        data.append({'id': x.id, 'name': "%s/%s" % (x.module.name, x.name)})

    data = json.dumps(data)
    return HttpResponse(data)


def Task(request, qs=""):

    from django.db.models import Q
    from packages.task.models import Task

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    try:
        issue = int(request.GET.get('issue'))
    except (ValueError, TypeError):
        issue = None

    data = []

    if issue is None:
        obj = Task.pp.filter(c_status=1).filter(Q(task__icontains=qs) | Q(issue__name__icontains=qs))[:25]
    else:
        obj = Task.pp.filter(c_status=1, issue__id=issue).filter(Q(task__icontains=qs) | Q(issue__name__icontains=qs))[:25]

    for val in obj:
        data.append({'id':val.id, 'name':"%s"%(val.task[:60])})

    data = json.dumps(data)

    return HttpResponse(data)


def TaskIssue(request):

    from django.db.models import Q
    from packages.task.models import Issue

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    qs = request.GET.get('qac')

    data = []
    obj = Issue.pp.filter(c_status=1).filter(Q(reference__icontains=qs) | Q(name__icontains=qs))[:25]
    for val in obj:
        data.append({'id': val.id, 'name': "%s" % (val.name[:60])})

    data = json.dumps(data)

    return HttpResponse(data)


def modules(request):

    from django.db.models import Q
    from packages.system.models import Module

    qs = request.GET.get('qac') or ""

    data = []
    obj = Module.objects.filter(Q(name__icontains=qs))[:25]
    for val in obj:
        data.append({'id': val.pk, 'name': "%s" % (val.name[:60])})

    data = json.dumps(data)

    return HttpResponse(data)


def contact(request):

    from django.db.models import Q
    from packages.system.models import Contact

    qs = request.GET.get('qac') or ""

    try:
        qm = request.GET.get('mode')
    except ValueError:
        qm = None

    if qm == 'all':
        data = None
        try:
            val = Contact.pp.get(name__iexact=qs)

            data = {
                'pk': val.pk,
                'name': val.name,
                'phone': val.phone,
                'email': val.email,
            }

        except Contact.DoesNotExist:
            pass

    elif qm is None:
        data = []
        obj = Contact.objects.filter(Q(name__icontains=qs) | Q(email__icontains=qs) | Q(phone__icontains=qs))[:25]
        for val in obj:
            data.append({'id': val.pk, 'name': "%s %s" % (val.name[:60], val.phone)})

    else:
        data = []
        for val in Contact.objects.filter(Q(name__icontains=qs) | Q(email__icontains=qs) | Q(phone__icontains=qs))[:25]:
            data.append("%s" % val.name)

    data = json.dumps(data)

    return HttpResponse(data)