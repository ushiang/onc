import os
# import threading
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
# from pyqrcode import QRCode
from packages.bin.auth import Auth
from packages.bin.lib import mkdir_if_not_exists

from packages.system.models import Module, Report as ReportModel


class Report:

    pdf = None
    file = None
    template = "prints/invoice.html"
    email_template = "email/basic_wrapper.html"
    filename = "tmp.pdf"
    html = "No data"
    request = None
    request_link = None
    reports = None

    title = None
    body = None
    footer = {'details': None, 'qrcode': None}
    company = {'logo': None, 'name': None, 'details': None, }
    order = {'id': None, 'barcode': None, 'date': None, 'terms': None, 'payment_method': None, 'shipping_method': None}
    to = {'name': None, 'details': None, 'photo': None, }
    table = {'headers': None, 'body': None, }
    person = None

    qrcode = None

    def __init__(self, title=None, footer=None, company=None, order=None, to=None, table=None, template=None,
                 filename=None, request=None, body=None, reports=None, person=None):

        self.title = title
        self.footer = footer if footer is not None else self.footer
        self.company = company if company is not None else self.company
        self.order = order if order is not None else self.order
        self.to = to if to is not None else self.to
        self.table = table if table is not None else self.table
        self.body = body
        self.person = person

        self.template = template if template is not None else self.template
        self.filename = filename if filename is not None else self.filename
        self.request = "http://" + request.META['HTTP_HOST'] if request else settings.BASE_URL
        self.reports = reports

        if filename:
            mkdir_if_not_exists("media/" + filename)

    def save(self):

        # create qrcode if qrcode is not none
        if self.footer:
            if self.footer['qrcode'] is not None:
                # qrc = QRCode(self.footer['qrcode'])
                self.qrcode = "%s/%s" % (settings.MEDIA_ROOT, self.filename.split('.pdf')[0]+".png")
                # qrc.png(self.qrcode, scale=9)
                self.footer['qrcode'] = self.qrcode

        data = {'report': self, }
        print data['report'].person
        template = get_template(self.template)
        self.html = template.render(Context(data))
        self.file = open(os.path.join(settings.MEDIA_ROOT, self.filename), "w+b")
        pisa.CreatePDF(self.html, dest=self.file, path=self.request_link)
        self.file.close()

        if self.qrcode:
            try:
                os.remove(self.qrcode)
            except OSError:
                pass

        return os.path.join(settings.MEDIA_ROOT, self.filename)

    def save_bulk(self):

        i = 0
        qrcodes = []
        for report in self.reports:
            # create qrcode if qrcode is not none
            if report['footer']['qrcode']:
                # qrc = QRCode(report['footer']['qrcode'])
                qrcode = "%s/%s" % (settings.MEDIA_ROOT, self.filename.split('.pdf')[0]+str(i)+".png")
                qrcodes.append(qrcode)
                # qrc.png(qrcode, scale=9)
                report['footer']['qrcode'] = qrcode
                i += 1

        data = {'reports': self.reports, }
        template = get_template(self.template)
        self.html = template.render(Context(data))
        self.file = open(os.path.join(settings.MEDIA_ROOT, self.filename), "w+b")
        pisa.CreatePDF(self.html, dest=self.file, path=self.request_link)
        self.file.close()

        for qrcode in qrcodes:
            print "deleting ", qrcode
            os.remove(qrcode)

        return True, os.path.join(settings.MEDIA_ROOT, self.filename)

    def render_pdf(self):
        r_file = open(os.path.join(settings.MEDIA_ROOT, self.filename), "r")
        pdf = r_file.read()
        r_file.close()
        return HttpResponse(pdf, content_type='application/pdf')

    def render_html(self):
        return HttpResponse(self.html)


class Basket(object):

    name = None
    file_url = None
    ext = None
    obj = None
    module = None
    request = None

    def __init__(self, request, module, name, file_url, ext=None):
        self.name = name
        self.file_url = file_url
        self.ext = ext or file_url.split('.')[len(file_url.split('.'))-1]
        self.module = module
        self.request = request

    def save(self):
        module = Module.objects.get(alias=self.module)
        me = Auth.whoami(self.request, "users")

        # let us correct the file url so it doesn't come with the entire file path, who needs that
        self.file_url = self.file_url.replace(os.path.join(settings.MEDIA_ROOT, ''), '')
        if self.file_url[0:6] == 'media/':
            self.file_url.replace('media/', '', 1)

        # let us now delete any previous report before creating a new one, to preserve precious server space
        reports = ReportModel.objects.filter(name=self.name, mac=me)
        for report in reports:
            report.delete()

        self.obj = ReportModel(module=module, name=self.name, file_url=self.file_url, ext=self.ext, mac=me)
        self.obj.save()
