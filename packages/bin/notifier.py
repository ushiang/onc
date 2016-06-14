from gettext import gettext as _
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Sum
from packages.system.models import Notification

NotificationTemplates = {
    'practitioner_credit_approval': _("Approve \? credit request"),
    'practitioner_asset_approval': _("You have \? pending asset approvals"),
    'practitioner_payment_approval': _("You have \? payments pending approval"),
}


class Notify():

    code = None
    msg = None
    number = 1
    pattern = None

    def __init__(self, code=None, number=1, pattern=None):
        self.code = code
        self.number = number
        self.pattern = pattern

    def notify(self):
        # get previous active notifications with same URL Patter
        try:
            notifications = Notification.objects.get(status=1, pattern=self.pattern)
            number = notifications.number
        except MultipleObjectsReturned:
            notifications = Notification.objects.filter(status=1, pattern=self.pattern)
            number = notifications.aggregate(total_number=Sum('number'))['total_number']
            notifications[1:].delete()
            notifications = notifications[0]
        except Notification.DoesNotExist:
            notifications = Notification()
            number = 0

        self.number += number

        notifications.number = self.number
        notifications.code = self.code
        notifications.pattern = self.pattern
        notifications.status = 1

        notifications.save()

    @staticmethod
    def drop(pattern, step=1):
        # get previous active notifications with same URL Patter
        try:
            notifications = Notification.objects.get(status=1, pattern=pattern)
            number = notifications.number
        except MultipleObjectsReturned:
            notifications = Notification.objects.filter(status=1, pattern=pattern)
            number = notifications.aggregate(total_number=Sum('number'))['total_number']
            notifications[1:].delete()
            notifications = notifications[0]
        except Notification.DoesNotExist:
            notifications = Notification()
            number = 0

        number -= step

        if number > 0:
            notifications.number = number
            notifications.save()
        else:
            try:
                notifications.delete()
            except AssertionError:
                pass

    @staticmethod
    def clear(pattern):
        # clear notifications matching the pattern
        Notification.objects.filter(pattern=pattern, status=1).update(status=0)

    @staticmethod
    def render():
        # build list of notifications for user's browser
        msgs = []
        notifications = Notification.objects.filter(status=1)
        for notification in notifications:
            msg = NotificationTemplates[notification.code].replace('\?', "<b>%s</b>" % notification.number)
            link = notification.pattern
            msgs.append('<li>'
                        '<a href="%s">'
                        '<span class="glyphicons glyphicons-history text-grey2 mr15"></span>%s</a>'
                        '</li>' % (link, msg))

        return notifications.aggregate(total=Sum('number'))['total'], "\n".join(msgs)