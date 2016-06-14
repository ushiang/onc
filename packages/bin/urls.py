from django.conf.urls import url
from packages.bin import autocomplete, select

#AUTOCOMPLETE PATTERNS
urlpatterns = [
                       
    #---------->>> PROFILE
    url(r'^json/profile/(?P<qs>[^/]+)$', autocomplete.Profile),
    url(r'^json/profile/$', autocomplete.Profile),

    #---------->>> LOCATION
    url(r'^json/location/(?P<qs>[^/]+)$', autocomplete.location),
    url(r'^json/location/$', autocomplete.location),

    #---------->>> INVENTORY ITEM
    url(r'^json/inventory/item/(?P<qs>[^/]+)$', autocomplete.InventoryItem),
    url(r'^json/inventory/item/$', autocomplete.InventoryItem),

    #---------->>> CRM CIM
    url(r'^json/crm/cim/(?P<qs>[^/]+)$', autocomplete.CRM_Profile),
    url(r'^json/crm/cim/$', autocomplete.CRM_Profile),

    #---------->>> TASK
    url(r'^json/task/(?P<qs>[^/]+)$', autocomplete.Task),
    url(r'^json/task/$', autocomplete.Task),

    #---------->>> TASK ISSUES
    url(r'^json/task/issue/(?P<qs>[^/]+)$', autocomplete.TaskIssue),
    url(r'^json/task/issue/$', autocomplete.TaskIssue),

    #---------->>> SYSTEM USERS
    url(r'^json/system/user/(?P<qs>[^/]+)$', autocomplete.User),
    url(r'^json/system/user/$', autocomplete.User),

    #---------->>> SYSTEM PRIVILEGES MANIFEST
    url(r'^json/system/privilege/manifest/(?P<qs>[^/]+)$', autocomplete.Privilege_Manifest),
    url(r'^json/system/privilege/manifest/$', autocomplete.Privilege_Manifest),

    #---------->>> SYSTEM PRIVILEGES USER CLASSES
    url(r'^json/system/privilege/user_class/(?P<qs>[^/]+)$', autocomplete.System_UserClass),
    url(r'^json/system/privilege/user_class/$', autocomplete.System_UserClass),

    #---------->>> SYSTEM MODULES
    url(r'^json/system/modules/(?P<qs>[^/]+)$', autocomplete.modules),
    url(r'^json/system/modules/$', autocomplete.modules),

    #---------->>> SYSTEM CONTACT
    url(r'^json/system/contact/$', autocomplete.contact),
]

# SELECT PATTERNS
urlpatterns += [
    #---------->>> HR ORGANIZATION
    url(r'^select/hr/office/$', select.SelectOffice),
    url(r'^select/hr/office/(?P<dept>\d+)/$', select.SelectOffice),
    url(r'^select/hr/office/(?P<dept>\d+)/(?P<office>\d+)/$', select.SelectOffice),

    #---------->>> INVENTORY SUB CATEGORY
    url(r'^select/inventory/subcategory/(?P<qs>[^/]+)/(?P<pk>[^/]+)$', select.SelectSubCategory),
    url(r'^select/inventory/subcategory/(?P<qs>[^/]+)/$', select.SelectSubCategory),
    url(r'^select/inventory/subcategory/(?P<qs>[^/]+)$', select.SelectSubCategory),
    url(r'^select/inventory/subcategory/$', select.SelectSubCategory),

    #---------->>> INVENTORY VENDOR
    url(r'^select/inventory/vendor/(?P<qs>[^/]+)$', select.SelectVendor),
    url(r'^select/inventory/vendor/$', select.SelectVendor),

    #---------->>> INVENTORY UOM
    url(r'^select/inventory/uom/(?P<qs>[^/]+)$', select.SelectUoM),
    url(r'^select/inventory/uom/$', select.SelectUoM),
]
