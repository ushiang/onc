import json
from django.utils.translation import gettext as _


class Month:
    month_name = [
        {'jan', 'January'},
        {'feb', 'February'},
        {'mar', 'March'},
        {'apr', 'April'},
        {'may', 'May'},
        {'jun', 'June'},
        {'jul', 'July'},
        {'aug', 'August'},
        {'sep', 'September'},
        {'oct', 'October'},
        {'nov', 'November'},
        {'dec', 'December'},
    ]
    month_code = ['01', '02', '03', '04', '05', '06', '07' '08', '09', '10', '11', '12']

    def __init__(self):
        pass


class Config:
    PAGE_LIMIT = 50

    def __init__(self):
        pass


class Defs:
    FormSuccess = {'status': 1, 'response': _('Completed successfully'), 'route': '', 'delay': 1000}
    FormError = {'status': 0, 'response': _('Some errors occurred. Failed to post'), 'route': '', 'delay': 20000}
    Info = {'status': 5, 'response': '', 'route': '', 'delay': 5000, 'style': 'info', 'command': None}
    Delete_Success = _("Deleted Successfully")
    Suspend_Success = _("Suspended Successfully")
    LiftSuspend_Success = _("Suspension Lifted Successfully")

    def __init__(self):
        pass