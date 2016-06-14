from django.conf.urls import url
from packages.system import views, privilege
from packages.system.controllers import UsersController
from packages.system.datatables import UsersTable

urlpatterns = [

    # JSON DATATABLEs
    url(r'^users/dt/users/$', UsersTable.as_view()),

    # LOGIN
    url(r'^login/$', views.login, name='login'),
    url(r'^login/(?P<q>[-\w+]+)/$', views.login, name='login'),

    # MISC
    url(r'^set-lang/(?P<lang>[-\w+]+)/$', views.select_language),
    url(r'^report/$', views.report_basket),
    url(r'^report/(?P<module>[-\w+]+)/$', views.report_basket),
    url(r'^report/delete/(?P<pk>\d+)/$', views.report_basket_delete),
    url(r'^report/delete/(?P<module>[-\w+]+)/(?P<pk>\d+)/$', views.report_basket_delete),
    url(r'^error/(?P<error>[-\w+]+)/$', views.auth_error),
    url(r'^notification-disperse/(?P<method>[-%\w+]+)/$', views.disperse_notification),
    url(r'^test-email/$', views.test_email),

    # USER MANAGEMENT
    url(r'^users/$', UsersController.as_view()),
    url(r'^users/(?P<method>[-\w+]+)/$', UsersController.as_view()),
    url(r'^users/(?P<method>[-\w+]+)/(?P<pk>\d+)/$', UsersController.as_view()),
    url(r'^users/(?P<method>[-\w+]+)/(?P<qk>\d+)/(?P<pk>\d+)/$', UsersController.as_view()),
    url(r'^users/(?P<method>[-\w+]+)/(?P<do>[-\w+]+)/(?P<pk>\d+)/$', UsersController.as_view()),
    url(r'^users/(?P<method>[-\w+]+)/(?P<do>[-\w+]+)/(?P<qk>\d+)/(?P<pk>\d+)/$', UsersController.as_view()),

    # PRIVILEGE MANAGEMENT
    url(r'^privilege/$', privilege.index),
    url(r'^privilege/module/$', privilege.module),
    url(r'^privilege/module/(?P<method>[-\w+]+)/$', privilege.module),
    url(r'^privilege/module/(?P<method>[-\w+]+)/(?P<pk>[-\w+]+)/$', privilege.module),
    url(r'^privilege/module-delete/(?P<pk>\d+)/$', privilege.module_delete),
    url(r'^privilege/module-delete/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.module_delete),

    # USER CLASS MANAGEMENT
    url(r'^privilege/user_class/$', privilege.user_class),
    url(r'^privilege/user_class/(?P<method>[-\w+]+)/$', privilege.user_class),
    url(r'^privilege/user_class/(?P<method>[-\w+]+)/(?P<pk>[-\w+]+)/$', privilege.user_class),
    url(r'^privilege/user_class-delete/(?P<pk>\d+)/$', privilege.user_class_delete),
    url(r'^privilege/user_class-delete/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.user_class_delete),

    # USER'S USER CLASS MANAGEMENT
    url(r'^privilege/uc_user/new/$', privilege.uc_user),
    url(r'^privilege/uc_user-delete/(?P<pk>\d+)/$', privilege.uc_user_delete),
    url(r'^privilege/uc_user-delete/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.uc_user_delete),

    # PRIVILEGE MANIFEST MANAGEMENT
    url(r'^privilege/manifest/$', privilege.manifest),
    url(r'^privilege/manifest/(?P<method>[-\w+]+)/$', privilege.manifest),
    url(r'^privilege/manifest/(?P<method>[-\w+]+)/(?P<pk>[-\w+]+)/$', privilege.manifest),
    url(r'^privilege/manifest-delete/(?P<pk>\d+)/$', privilege.manifest_delete),
    url(r'^privilege/manifest-delete/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.manifest_delete),

    # USER CLASS PRIVILEGE MANAGEMENT
    url(r'^privilege/new/$', privilege.ucp),
    url(r'^privilege/flush/(?P<pk>\d+)/$', privilege.ucp_flush),
    url(r'^privilege/flush/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.ucp_flush),

    # USERS' PRIVILEGE MANAGEMENT
    url(r'^privilege/users_privilege/$', privilege.user_class),
    url(r'^privilege/users_privilege/(?P<method>[-\w+]+)/$', privilege.user_class),
    url(r'^privilege/users_privilege/(?P<method>[-\w+]+)/(?P<pk>[-\w+]+)/$', privilege.user_class),
    url(r'^privilege/users_privilege-delete/(?P<pk>\d+)/$', privilege.user_class_delete),
    url(r'^privilege/users_privilege-delete/(?P<process>[-\w+]+)/(?P<pk>\d+)/$', privilege.user_class_delete),
]
