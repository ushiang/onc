import os
import shutil
import threading
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template


class Email(object):

    to = None
    from_email = None
    subject = None
    body = None
    footer = None
    files = None
    email_template = "email/basic_wrapper.html"
    thread = None
    data = dict()
    request = None

    auth_email = None
    auth_password = None
    smtp_host = None
    smtp_port = None
    use_tls = False

    # establish thread for send emails
    class EmailThread(threading.Thread):
        def __init__(self, name, calling_object):
            threading.Thread.__init__(self)
            self.name = name
            self.obj = calling_object

        def run(self):
            print "Email thread started at %s" % datetime.now()
            start_time = datetime.now()
            self.obj.process()
            print "Email Thread [%s] has finished at %s, duration %s seconds " \
                  % (self.name, datetime.now(), (datetime.now() - start_time).seconds)

    def __init__(self, request, from_email=None, to=None, subject=None, body=None, footer=None, files=None, data=None):
        self.from_email = from_email
        self.to = to
        self.subject = subject if subject else "No Subject"
        self.body = body
        self.footer = footer
        self.files = files or []
        self.data = data
        self.request = request

        self.data['base_url'] = 'http://' + self.request.META['HTTP_HOST'] + '/'

    def send(self):
        print "sending email..."
        self.thread = self.EmailThread("Email_thread", self)
        self.thread.start()

    def process(self):

        files_to_delete = []

        from_email = self.from_email or settings.EMAIL_HOST_USER
        email_template = get_template(self.email_template)
        html_content = email_template.render(Context(self.data))

        if settings.EMAIL_DEBUG:
            print "Sending debug mail"
            self.to = ["pukonu@gmail.com"]

        if self.auth_email:
            print "custom mail"
            print self.auth_email
            from_email = self.auth_email
            msg = EmailMessage(self.subject, html_content, from_email, self.to)
            msg.connection = get_connection(username=self.auth_email, password=self.auth_password,
                                            host=self.smtp_host, port=self.smtp_port, use_tls=self.use_tls)

        else:
            msg = EmailMessage(self.subject, html_content, from_email, self.to)

        print "Send to: %s " % self.to

        for filename in self.files:
            # lets make a copy of the file and delete soon after sending
            ext = filename['path'].split('.')[len(filename['path'].split('.'))-1]
            friendly = "%s.%s" % (filename['friendly'], ext)
            src = os.path.join(settings.MEDIA_ROOT, filename['path'])
            dst = os.path.join(settings.MEDIA_ROOT, friendly)
            shutil.copyfile(src, dst)
            msg.attach_file(os.path.join(settings.MEDIA_ROOT, dst))
            files_to_delete.append(dst)

        msg.content_subtype = "html"
        msg.send()

        # let remove the duplicate files
        for filename in files_to_delete:
            print "deleting %s" % filename
            os.path.exists(filename) and os.remove(filename)

    def preview(self):
        email_template = get_template(self.email_template)
        html_content = email_template.render(Context(self.data))

        return HttpResponse(html_content)