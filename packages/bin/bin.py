from django import forms


class Page(object):
    page_title = None
    title = None
    icon = None
    description = None
    comprehension = None
    form_name = None
    form_action = None
    breadcrumbs = None
    request = None
    id = None
    errors = None
    link_root = ""
    confirmation_value = "Confirm Delete!"
    non_field_errors = []
    action = None
    paginator = None
    paginator_str = None
    paginator_index = None
    query_string = None

    def __init__(self, request):
        self.request = request


class Table(object):
    name = None
    cols = None
    rows = None
    obj = None


class Actions(object):
    
    class Icon(object):
        pass
    
    setattr(Icon, 'edit', 'fa fa-pencil')
    setattr(Icon, 'delete', 'fa fa-times')
    setattr(Icon, 'activate', 'fa fa-check')


class ActionButton(object):
    edit = 'fa fa-pencil'
    delete = 'fa fa-times'
    activate = 'fa fa-check'


class FormApproval(forms.Form):
    comment = forms.CharField(
        label='Comment',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment here', 'rows': 3})
    )


def format_date(obj, format_str="%b %d, %Y", format_datetime="%b %d, %Y %H:%M"):
    from datetime import datetime, date
    try:
        if type(obj) == date:
            x = obj.strftime(format_str)
        elif type(obj) == datetime:
            x = obj.strftime(format_datetime)
        else:
            x = ""
    except TypeError:
        x = ""

    return x


def format_status(value, default_dict=None):
    if not default_dict:
        default_dict = {
            "": {'label': "Unknown", 'style': 'alert'},
            None: {'label': "Unknown", 'style': 'alert'},
            0: {'label': "Inactive", 'style': 'danger'},
            1: {'label': "Active", 'style': 'success'},
            2: {'label': "Warning", 'style': 'warning'},
        }

    return "<span class='label label-%s'>%s</label>" % (default_dict[value]['style'], default_dict[value]['label'])


def format_alias(value):
    params = ['-', '/', '\\', '|', '"', "'", '+', '!', '`', '~', '(', ')', '[', ']', '~', '{', '}']

    for param in params:
        value = value.replace(param, '_')

    return value.replace(' ', '').lower()


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