import json
import re

from django.utils.translation import gettext as _
from packages.bin import dictionary


def form_meta(fields):
    tmp = []
    tmp2 = []
    for field in fields:
        tmp.append(''''%s': forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}),''' % field)
        tmp2.append(''''%s': "%s",''' % (field, field.title()))


def format_form_error(form):
    regex = re.compile("<[^<]+?>", re.IGNORECASE)
    ret = []
    for x in form.errors:
        label = form.fields[x].label
        data = "%s [%s]" % (form.errors[x], _(label))
        ret.append(regex.sub('', str(data)))

    return ret


def value_separator(value):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US')
    return locale.format("%d", value, grouping=True)


def number_choice(start=1, end=100, step=1, r_type=str, empty_string=None):

    objects = range(start, end+1)[::step]
    choice = []

    if empty_string:
        choice.append(('', empty_string))

    for obj in objects:
        choice.append((r_type(obj), r_type(obj)))

    return tuple(choice)


def month_choice():
    choice = (
        ('', _('Select a month')),
        ('1', _('January')),
        ('2', _('February')),
        ('3', _('March')),
        ('4', _('April')),
        ('5', _('May')),
        ('6', _('June')),
        ('7', _('July')),
        ('8', _('August')),
        ('9', _('September')),
        ('10', _('October')),
        ('11', _('November')),
        ('12', _('December')),
    )

    return choice


def given_year(start=1970, end=2048, extra=1):
    from datetime import datetime

    if end == 'now':
        end = int(datetime.now().year) + extra
    
    default = datetime.now().year
    choices = number_choice(start, end)
    
    return choices, default


def given_month():
    from datetime import datetime
    from packages.bin.dictionary import Month
    
    current_month = datetime.now().month
    default = Month.month_name[current_month-1]
    choices = []
    
    for month in Month.month_name:
        choices.append((month, month),)
    
    return tuple(choices), default


def path_and_rename(instance, filename):
    import hashlib
    import datetime
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(instance.reference + str(datetime.datetime.now())).hexdigest() + ext
    return '/'.join(['shareware/dmc/hr/photos', filename])


def cert_path_and_rename(instance, filename):
    import hashlib,datetime
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(instance.profile.reference + str(datetime.datetime.now())).hexdigest() + ext
    return '/'.join(['shareware/dmc/hr/certificate', filename])


def get_thumb(path, version='128x128'):
    ext = '.' + path.split('.')[-1]
    filename = "".join(path.split('.')[:-1])
    return filename + '.' + version + ext


def get_query_string(request):
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']

    return queries_without_page


def drop_down(data, default=None, element_id=None, row=0):

    s = ''
    n = 0

    for instance in data:
        for x, y in instance.items():
            if str(default) == str(x):
                s += '''<option value="%s_%s" selected="selected">%s</option>''' % (n, x, y)
            else:
                s += '''<option value="%s_%s">%s</option>''' % (n, x, y)

            n += 1

    obj = '''<select id="{element_id}" name="{element_id}" class="form-control {element_id} pp-drop-down"
                data-row="{row}">
        {val}
    </select>'''.format(element_id=element_id, val=s, row=row)

    return obj


def response_success(route='', response=None, delay=1000, status=1, modal=False):
    res = dictionary.Defs().FormSuccess
    res['route'] = route
    res['delay'] = delay
    res['response'] = response if response is not None else res['response']
    res['status'] = status
    res['modal'] = str(modal).lower()

    return json.dumps(res)


def response_error(response, route=''):
    res = dictionary.Defs().FormError

    if type(response).__name__ == 'str' or type(response).__name__ == 'unicode':
        res['route'] = route
        res['response'] = response

    else:
        i = 1
        response_str = ""
        if response:
            for y in response:
                for x in y:
                    response_str += "%s. %s<br/>" % (str(i), x)
                    i += 1
        else:
            response_str = res['response']

        res['route'] = route
        res['response'] = response_str

    return json.dumps(res)


def response_generic(response, route=None, style=None, delay=None, command=None):
    res = dictionary.Defs().Info

    if type(response).__name__ == 'str' or type(response).__name__ == 'unicode':
        response_str = response

    else:
        i = 1
        response_str = ""
        for y in response:
            for x in y:
                response_str += "%s. %s<br/>" % (str(i), x)
                i += 1

    res['route'] = route
    res['response'] = response_str
    res['style'] = style if style else res['style']
    res['delay'] = delay if delay else res['delay']
    res['command'] = command if command else res['command']

    return json.dumps(res)


def random_chars(size, chars=None):
    """
    Use like this next(random_chars(220)) to generate
    :param size: int
    :param chars: string sub class
    """
    import random
    from string import ascii_uppercase, ascii_lowercase, digits
    from itertools import islice

    if chars == 'alphanumeric':
        chars = (ascii_lowercase + digits)
    elif chars == 'text':
        chars = ascii_lowercase
    elif chars == 'number':
        chars = digits
    else:
        chars = (ascii_uppercase + ascii_lowercase + digits)

    selection = iter(lambda: random.choice(chars), object())
    while True:
        yield ''.join(islice(selection, size))


def autocomplete_state(queryset=None, instance_var=None, url=None, element=None, token=1, theme='wit2', enclose=True):

    if instance_var is None or instance_var == []:
        json_object = ""

    elif token > 1:
        try:
            try:
                tmp = instance_var
            except (ValueError, AttributeError):
                tmp = ""

            if type(tmp) == str or type(tmp) == unicode:
                m_objects = tmp.split(',')
            else:
                m_objects = []
                for m_object in tmp:
                    m_objects.append(m_object.id)

            arr = []
            for m_object in m_objects:
                r_object = queryset.get(id=m_object)
                arr.append('''{'id':'%s', 'name':"%s"}''' % (str(m_object), r_object))

            json_object = ''', prePopulate: [%s]''' % (','.join(arr)) if arr else ""

        except (ValueError, UnboundLocalError):
            json_object = ""

    else:
        try:
            json_object = ''', prePopulate: [{'id':'%s', 'name':'%s'}]''' % (str(instance_var.id), instance_var)

        except (ValueError, UnboundLocalError):
            json_object = ""

    #script for form

    if enclose:
        tag_open = "<script>"
        tag_close = "</script>"
    else:
        tag_open = tag_close = ""

    script = '''
    %s
    $(document).ready(function(){
        $('#%s').tokenInput('%s', {theme:'%s', tokenLimit:%s, hintText:'Start typing name' %s});
    });
    %s''' % (tag_open, element, url, theme, token, json_object, tag_close)

    return script


def mkdir_if_not_exists(path):
    import os

    directory = "/".join(path.split('/')[0:len(path.split('/'))-1])
    if not os.path.exists(directory):
        os.makedirs(directory)


def password_checker(password, min_strength=3, forbidden=list()):

    import re

    error = None

    password_strength = dict.fromkeys(['has_upper', 'has_lower', 'has_num', 'has_length'], False)

    # check against forbidden list
    if password in forbidden:
        error = _('Your password cannot be <b>"%s"</b>' % password)

    if 6 <= len(password) < 12:
        password_strength['has_length'] = True
    if re.search(r'[A-Z]', password):
        password_strength['has_upper'] = True
    if re.search(r'[a-z]', password):
        password_strength['has_lower'] = True
    if re.search(r'[0-9]', password):
        password_strength['has_num'] = True

    score = len([b for b in password_strength.values() if b])

    if score >= min_strength:
        return True, None
    else:
        return False, error


def encrypt_password(password):
    from hashlib import sha1
    return sha1(password).hexdigest()


def escape(value):
    from django.utils.html import escape as html_escape, strip_tags

    if value:
        value = html_escape(strip_tags(value))
    return value


def empty(value, strict=False):
    if (value is None or value == "" or value == 0) and strict:
        return True
    elif value is None or value == "":
        return True
    else:
        return False


def timesince(dt, default="just now"):
    import pytz
    from datetime import datetime

    now = pytz.utc.localize(datetime.now())

    if dt > now:
        return _("time in future")

    diff = now - dt
    periods = (
        (diff.days/365, _("year"), _("years")),
        (diff.days/30, _("month"), _("months")),
        (diff.days/7, _("week"), _("weeks")),
        (diff.days, _("day"), _("days")),
        (diff.seconds/3600, _("hour"), _("hours")),
        (diff.seconds/60, _("minute"), _("minutes")),
        (diff.seconds, _("second"), _("seconds")),
    )
    for period, singular, plural in periods:
        if period:
            return _("%d %s ago") % (period, singular if period == 1 else plural)

    return default
