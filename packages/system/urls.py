from django.conf.urls import patterns, url
from packages.system import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, name='login'),
    url(r'^login/(?P<q>[-\w+]+)/$', views.login, name='login'),
    url(r'^destroy-session/$', views.logout, name='logout'),
    
    #--------->>>USER MANAGEMENT
    url(r'^users/$', views.User),
    url(r'^users/new/$', views.UserManage),
    url(r'^users/update/(?P<pk>[-\w+]+)/$', views.UserManage),
    url(r'^users/delete/(?P<pk>[-\w+]+)/$', views.UserDelete),
    url(r'^users/delete/(?P<process>[-\w+]+)/(?P<pk>[-\w+]+)/$', views.UserDelete),
    
    url(r'^users/reset-password/(?P<pk>[-\w+]+)/$', views.UserResetPassword),
    url(r'^users/reset-password/(?P<process>[-\w+]+)/(?P<pk>[-\w+]+)/$', views.UserResetPassword),
    
    url(r'^users/status/(?P<method>[-\w+]+)/(?P<pk>[-\w+]+)/$', views.UserStatus),
)