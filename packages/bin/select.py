import json, urllib

from packages.bin.auth import Auth

from django.http import HttpResponse
from django import forms


#===============================================================================
# HR - ORGANIZATION - OFFICE
#===============================================================================

def SelectOffice(request, qs=None):

    s = Auth().isAuth(request)
    if not s:
        return Auth.routeLogin

    from packages.hr.hr_organization.models import Office
    
    qs = "" if qs is None else urllib.unquote(qs)
    
    #---------->>> Create Form
    class FormSelectOffice(forms.Form):
        office = forms.ModelChoiceField(queryset=Office.objects.filter(department__pk=qs))
        office.widget.attrs.update({'class':'form-control pp-chosen'})
    
    form = FormSelectOffice()
    
    return HttpResponse(form)


#===============================================================================
# INVENTORY - CATEGORY - SUB CATEGORY
#===============================================================================

def SelectSubCategory(request, qs=None, pk=None):

    s = Auth().isAuth(request)
    if not s:
        return Auth.routeLogin

    from packages.inventory.inventory_category.models import SubCategory

    qs = "" if qs is None else urllib.unquote(qs)

    class FormSelectSubCategory(forms.Form):
        sub_category = forms.ModelChoiceField(queryset=SubCategory.objects.filter(category__pk=qs))
        sub_category.widget.attrs.update({'class':'form-control pp-chosen'})

    form = FormSelectSubCategory(initial = {'sub_category': pk })

    return HttpResponse(form)


#===============================================================================
# INVENTORY - CATEGORY - UNIT OF MEASURE
#===============================================================================

def SelectUoM(request, qs=None):

    s = Auth().isAuth(request)
    if not s:
        return Auth.routeLogin

    from packages.inventory.inventory_item.models import UoM

    qs = "" if qs is None else urllib.unquote(qs)

    class FormSelectUoM(forms.Form):
        uom = forms.ModelChoiceField(queryset=UoM.objects.filter(item__id=qs))
        uom.widget.attrs.update({'class':'form-control pp-chosen'})

    return HttpResponse(FormSelectUoM())


#===============================================================================
# INVENTORY - CATEGORY - VENDOR
#===============================================================================

def SelectVendor(request, qs=None):

    s = Auth().isAuth(request)
    if not s:
        return Auth.routeLogin

    from packages.inventory.inventory_item.models import Item

    qs = "" if qs is None else urllib.unquote(qs)

    class FormSelectVendor(forms.Form):
        vendor = forms.ModelChoiceField(queryset=Item.objects.filter(id=qs)[0].vendor.all())
        vendor.widget.attrs.update({'class':'form-control pp-chosen'})

    return HttpResponse(FormSelectVendor())