__author__ = 'prologic'

from django.db import models
from django.http import HttpResponseRedirect


class SysLicense(object):
    lid = "20160426"
    sys = "BDGT"

    @staticmethod
    def process_request(request):
        try:
            SysLicense.lid = request.session['lid']
            SysLicense.sys = request.session['sys']
        except KeyError:
            pass


class PostPrincipal(models.Manager):
    def get_queryset(self):
        return super(PostPrincipal, self).get_queryset().filter(lid=SysLicense.lid, sys=SysLicense.sys)