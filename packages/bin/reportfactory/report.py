import os
import threading
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
from pyqrcode import QRCode


class Report:

    pdf = None
    file = None
    template = "prints/invoice.html"
    email_template = "email/basic_wrapper.html"
    filename = "tmp.pdf"
    html = "No data"
    request = None

    title = None
    footer = {'details': None, 'qrcode': None}
    company = {'logo': None, 'name': None, 'details': None, }
    order = {'id': None, 'barcode': None, 'date': None, 'terms': None, 'payment_method': None, 'shipping_method': None}
    to = {'name': None, 'details': None, 'photo': None, }
    table = {'headers': None, 'body': None, }

    def __init__(self, title=None, footer=None, company=None, order=None, to=None, table=None, template=None,
                 filename=None, request=None):

        self.title = title
        self.footer = footer if footer is not None else self.footer
        self.company = company if company is not None else self.company
        self.order = order if order is not None else self.order
        self.to = to if to is not None else self.to
        self.table = table if table is not None else self.table

        self.template = template if template is not None else self.template
        self.filename = filename if filename is not None else self.filename
        self.request = request

        # create qrcode if qrcode is not none
        if footer['qrcode'] is not None:
            qrc = QRCode(footer['qrcode'])
            qrcode = "%s/%s" % (settings.MEDIA_ROOT, self.filename.split('.pdf')[0]+".png")
            qrc.png(qrcode, scale=9)
            footer['qrcode'] = qrcode

    def save(self):
        data = {'report': self, }
        template = get_template(self.template)
        self.html = template.render(Context(data))
        self.file = open(os.path.join(settings.MEDIA_ROOT, self.filename), "w+b")
        pisa.CreatePDF(self.html, dest=self.file, path="http://%s/" % self.request.META['HTTP_HOST'])
        self.file.close()

        return self.pdf

    def email(self, to, subject=None, body=None, footer=None):
        from django.core.mail import EmailMessage
        from datetime import datetime

        filename = self.filename

        def send(to, subject=None, body=None, footer=None):
            subject = subject if subject is not None else "No Subject"
            body = body if body is not None else ""
            footer = footer if footer is not None else ""

            data = {
                'header': subject,
                'body': body,
                'footer': footer,
            }

            if type(to) == str or type(to) == unicode:
                to = to.split(',')

            from_email = settings.EMAIL_HOST_USER
            email_template = get_template(self.email_template)
            html_content = email_template.render(Context(data))

            msg = EmailMessage(subject, html_content, from_email, to)
            msg.content_subtype = "html"
            msg.attach_file(os.path.join(settings.MEDIA_ROOT, filename))
            msg.send()

        # establish thread for send emails
        class EmailThread(threading.Thread):
            def __init__(self, name, to, subject=None, body=None, footer=None):
                threading.Thread.__init__(self)
                self.name = name
                self.to = to
                self.subject = subject
                self.body = body
                self.footer = footer

            def run(self):
                start_time = datetime.now()
                print "Started a new thread [%s] at %s " % (self.name, start_time)
                send(self.to, self.subject, self.body, self.footer)
                print "Thread [%s] has finished at %s, duration %s seconds " \
                      % (self.name, datetime.now(), (datetime.now() - start_time).seconds)

        my_thread = EmailThread("email_thread", to, subject, body, footer)
        my_thread.start()

        return True

    def render_pdf(self):
        r_file = open(os.path.join(settings.MEDIA_ROOT, self.filename), "r")
        pdf = r_file.read()
        r_file.close()
        return HttpResponse(pdf, content_type='application/pdf')

    def render_html(self):
        return HttpResponse(self.html)