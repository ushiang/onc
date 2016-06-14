from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from packages.bin.email import Email


class HRNotify(object):

    obj = None
    officer = None
    method = None
    comment = None
    subject = None
    title = None
    msg = None
    link = None
    to = None
    about = None
    me = None
    request = None
    picture = None
    email = []
    template = None
    company = None

    # notifications class
    n_name = None
    n_note = None
    n_link = None
    n_handle = None

    def __init__(self, obj=None):
        self.obj = obj

    def add(self):
        from packages.system.models import Module, Notification

        # do system notifications
        if self.n_name:
            module = Module.objects.get(alias="human_resource")

            n, c = Notification.pp.get_or_create(name=self.n_name, module=module, handle=self.to)
            if c:
                n.save()

            if self.n_note:
                n.note = self.n_note
            else:
                n.note = self.msg

            n.link = self.link
            n.subscription_handle = self.n_handle
            n.status = 1
            n.save()

    @staticmethod
    def disperse(request, link, module_name=None):
        from packages.bin.auth import Auth
        from packages.system.models import Notification, Module

        me = Auth.whoami(request)

        if module_name is not None:
            module = Module.objects.get(alias=module_name)
            Notification.pp.filter(module=module, link=link, handle=me).update(status=0)
        else:
            Notification.pp.filter(link=link, handle=me).update(status=0)

    def notify(self):
        """
        Notify officer of leave application, approvals and handover notes
        Method are application, higher level, lower level, handover note, proceed, hr_copy, back from leave, e.t.c
        :return:
        """
        from datetime import date
        from packages.bin.auth import Auth

        # select a default template if template is None
        if self.template is None:
            self.template = "system/email/generic.html"

        # do system notification
        self.add()

        # do email notifications
        me = Auth.whoami(self.request)
        company = get_company(user=me)

        # send mail
        data = dict()
        data['request'] = self.request
        data['company'] = company

        try:
            data['logo'] = company.company_logo_raw.url
        except (ValueError, AttributeError):
            data['logo'] = ""

        data['email'] = me.email
        data['link'] = self.link
        data['title'] = self.title
        data['info'] = self.msg
        data['picture'] = self.picture
        data['date'] = format_date(date.today(), "%B %d, %Y")

        subject = _("%s - %s" % (self.title, company.company_name))

        if self.to:
            if type(self.to) is list:
                for x in self.to:
                    if x.email:
                        self.email.append(x.email)
            else:
                self.email.append(self.to.email)

            if settings.EMAIL_DEBUG:
                self.email = ["pukonu@gmail.com"]

            email_object = Email(self.request, from_email=company.auth_email, to=self.email,
                                 subject=subject, data=data)
            email_object.email_template = self.template
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            email_object.send()

            return email_object.preview()

    def notify_all(self):
        """
        Notify officer of leave application, approvals and handover notes
        Method are application, higher level, lower level, handover note, proceed, hr_copy, back from leave, e.t.c
        :return:
        """
        from packages.bin.auth import Auth
        from datetime import date
        from packages.hr.hr_personnel.models import Basic

        # do email notifications
        me = Auth.whoami(self.request)
        company = get_company(user=me)

        for profile in Basic.pp.filter(status=1):

            # send mail
            data = dict()
            data['request'] = self.request
            data['company'] = company

            try:
                data['logo'] = company.company_logo_raw.url
            except (ValueError, AttributeError):
                data['logo'] = ""

            data['email'] = profile.email
            data['link'] = self.link
            data['title'] = self.title
            data['info'] = self.msg
            data['picture'] = self.about.get_image_url_l()
            data['profile'] = profile
            data['profile_alt'] = self.about
            data['date'] = format_date(date.today(), "%B %d, %Y")

            subject = _("%s - %s" % (self.title, company.company_name))

            if settings.EMAIL_DEBUG:
                to = "pukonu@gmail.com"
            else:
                to = profile.email

            email_object = Email(self.request, from_email=company.auth_email, to=[to],
                                 subject=subject, data=data)
            email_object.email_template = self.template
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            email_object.send()

            #return email_object.preview()


class Page(object):
    page_title = None
    table_title = None
    title = None
    icon = None
    description = None
    comprehension = None
    form_name = None
    form_action = None
    breadcrumbs = None
    request = None
    id = None
    pk = None
    qk = None
    update = None
    errors = None
    link_root = ""
    confirmation_value = _("Confirm Delete!")
    confirmation_theme = "alert alert-warning"
    confirmation_icon = "fa fa-trash"
    non_field_errors = []
    data = {}
    action = None
    paginator = None
    paginator_str = None
    paginator_index = None
    query_string = None
    theme = 'danger'
    script = ''
    script2 = ''
    method = None
    request = None

    def __init__(self, request):
        self.request = request


class Table(object):
    name = None
    cols = None
    rows = None
    obj = None
    settings = None


class Actions(object):
    
    class icon(object):
        pass

    setattr(icon, 'edit', 'fa fa-pencil')
    setattr(icon, 'delete', 'fa fa-times')
    setattr(icon, 'activate', 'fa fa-check')


class ActionButton(object):
    edit = 'fa fa-pencil'
    delete = 'fa fa-times'
    activate = 'fa fa-check'


class NavButtonFactory(object):
    obj = []
    button_dict = {
        'left': '<span data-toggle="tooltip" title="{0}" class="fa fa-chevron-left"></span>'.
        format(_("Previous Record")),
        'table': '<span data-toggle="tooltip" title="{0}" class="fa fa-table"></span>'.format(_("Table View")),
        'grid': '<span data-toggle="tooltip" title="{0}" class="fa fa-th-large"></span>'.format(_("Grid View")),
        'form': '<span data-toggle="tooltip" title="{0}" class="fa fa-edit"></span>'.format(_("Form View")),
        'graph': '<span data-toggle="tooltip" title="{0}" class="fa fa-bar-chart-o"></span>'.format(_("Analytics")),
        'right': '<span data-toggle="tooltip" title="{0}" class="fa fa-chevron-right"></span>'.format(_("Next Record")),
    }


def table_button(settings):
    button = ""
    button += '<div class="btn-group">'
    for setting in settings:
        button += ' <a type="button" href="#{0}" ' \
            'class="btn btn-default btn-gradient btn-xs">'.format(setting['link'])
        button += '<span class="{0}"></span></a>'.format(setting['icon'])

    button += '</div>'

    return button


def table_dropdown(settings):
    button = ""
    button += '<div class="btn-group">'
    button += '<button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" ' \
              'aria-expanded="false">%s<span class="caret ml5"></span></button>' % _('Actions')
    button += '<ul class="dropdown-menu pull-right" role="menu">'

    for setting in settings:

        try:
            attr = setting['attr']
        except KeyError:
            attr = ""

        button += '<li><a ui-WitMVC-href href="#%(link)s" %(attr)s>%(label)s</a></li>' % {
            'link': setting['link'],
            'label': setting['label'],
            'attr': attr,
        }

    button += '</ul></div>'

    return button


def get_all_images(filename, ext, sizes=list()):

    if not sizes:
        sizes.append('64x64')
        sizes.append('128x128')
        sizes.append('256x256')
        sizes.append('512x512')
        sizes.append('1024x1024')

    fn = list()
    fn.append(settings.MEDIA_ROOT + '/' + filename + ext)
    for s in sizes:
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.' + s + ext)

    return fn


def get_generic_thumb(size='128x128', style=2):
    return '/media/avatar/{style}/{size}.jpg'.format(style=style, size=size)


def get_root_url(request):
    return 'http://' + request.META['HTTP_HOST'] + '/'


def get_media_root_url(request):
    return 'http://' + request.META['HTTP_HOST'] + '/media/'


def format_date(obj, format="%b %d, %Y", format_datetime="%b %d, %Y %H:%M", empty_value=None):
    from datetime import datetime, date
    try:
        if type(obj) == date:
            x = obj.strftime(format)
        elif type(obj) == datetime:
            x = obj.strftime(format_datetime)
        else:
            x = empty_value
    except:
        x = empty_value

    return x


def format_status(value, default_dict=None):
    if not default_dict:
        default_dict = {
            "": {'label': _("Unknown"), 'style': 'alert'},
            None: {'label': _("Unknown"), 'style': 'alert'},
            0: {'label': _("Inactive"), 'style': 'danger'},
            1: {'label': _("Active"), 'style': 'success'},
            2: {'label': _("Warning"), 'style': 'warning'},
        }

    return "<span class='label label-%s'>%s</label>" % (default_dict[value]['style'], default_dict[value]['label'])


def format_alias(value, params=None):
    params = ['-', '/', '\\', '|', '"', "'", '+', '!', '`', '~', '(', ')', '[', ']', '~', '{', '}', ' ']

    for param in params:
        value = value.replace(param, '_')

    value = value.replace('__', '_').replace('__', '_').lower()

    return value


def bts(request):
    try:
        request.session["refer"]
    except KeyError:
        request.session["refer"] = "/hr/profile/"

    ref = request.session["refer"]

    return ref


def get_week_first_and_last_day(year, week):
    """
    This function returns a tuple of the first and last day of a given year, week
    :param year:
    :param week:
    :return: tuple
    """
    from datetime import date, timedelta

    week += 1
    d = date(year, 1, 1)
    if d.weekday() > 3:
        d = d+timedelta(7-d.weekday())
    else:
        d = d - timedelta(d.weekday())
        dlt = timedelta(days=((week-1)*7))

    return d + dlt - timedelta(days=1),  d + dlt + timedelta(days=6) - timedelta(days=1)


def get_date_range(start, end, workdays=None, holidays=None, skip_non_workdays=True):
    """
    This function calculates the durations between 2 dates skipping days as in the params when call
    :rtype : tuple
    :param start: date
    :param end: date
    :param workdays: string [Comma Separated Values, 0 - Monday through to 6 - Sunday]
    :param holidays: list
    :param skip_non_workdays: boolean
    :return:
    """
    from datetime import timedelta

    duration = 0

    # define workdays
    if workdays is None:
        workdays = [0, 1, 2, 3, 4]
    else:
        workdays = workdays.split(",")

    # check if we need to skip non workdays
    if skip_non_workdays is False:
        workdays = [0, 1, 2, 3, 4, 5, 6]

    # validate dates
    if end < start:
        return False, _("End date is before start date")

    # now its time for us to iterate
    i = start
    while i <= end:

        # first let give benefit of the doubt
        incr = True

        # lets see if day is in the workday array if not then fault it existence here
        try:
            workdays.index(i.weekday())
        except ValueError:
            incr = False

        # lets check if day is an holiday, charge guilty if so.
        # We are checking the index in holiday array
        try:
            holidays.index(i)
            incr = False
        except (ValueError, AttributeError):
            pass

        if incr:
            duration += 1
            #print "This day passed the criterion %s" % i

        i += timedelta(1)

    return True, duration


def dyna_table(data):

    content = []
    for x in data:
        content.append('<li class="col-md-4 span4" data-color="gray">%s</li>' % x)

    tmp = '''
        <ul id="ul-dynatable" class="fluid row-fluid">
            %s
        </ul>''' % "".join(content)

    return tmp


def get_company(request=None, user=None):
    from packages.bin.auth import Auth
    from packages.system.models import License

    if user is not None:
        me = user
    else:
        try:
            me = Auth.whoami(request)
        except ObjectDoesNotExist:
            return None

    company = License.objects.get(lid=me.lid, sys=me.sys)

    return company


def get_week_range(day):

    from datetime import timedelta

    weekday = day.isoweekday()

    if weekday < 7:
        start = day - timedelta(weekday)
        end = day + timedelta(6-weekday)
    else:
        start = day
        end = day + timedelta(6)

    return (start, end)
