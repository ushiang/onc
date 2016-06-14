from django.conf.urls import patterns, url
from packages.bin import autocomplete, select

#AUTOCOMPLETE PATTERNS
urlpatterns = patterns('',
                       
    #---------->>> PROFILE
    url(r'^json/profile/(?P<qs>[^/]+)$', autocomplete.Profile),
    url(r'^json/profile/$', autocomplete.Profile),
)