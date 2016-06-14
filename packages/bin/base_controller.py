from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.views.generic import View


class BaseController(View):

    base_url = ""
    base_template = ""

    second_base = ""
    second_base_alt = ""

    page = None
    template = None
    model = None
    form_obj = None
    form = None
    instance = None
    old_instance = None
    datatable_url = None

    me = None

    def set_template(self, *args, **kwargs):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]).replace("/", ""))
            i += 1

        self.template = self.base_template + "/".join(tmp)

        print self.template

        try:
            self.page.second_base = kwargs["second_base"] + "/"
        except KeyError:
            self.page.second_base = self.second_base_alt

        try:
            self.page.base_template = kwargs["base_template"] + "/"
        except KeyError:
            self.page.base_template = self.base_template

    def set_menu(self, *args, **kwargs):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]).replace("/", ""))
            i += 1

        try:
            base_template = kwargs["base_template"] + "/"
        except KeyError:
            base_template = self.base_template

        self.page.menu = base_template + "/".join(tmp)

    def set_form_action(self, *args):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]).replace("/", ""))
            i += 1

        self.page.form_action = self.base_url + "/".join(tmp) + "/"

    def set_rest_link(self, *args):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]))
            i += 1

        self.page.rest_link = self.base_url + "/".join(tmp) + "/"

    def set_datatable_url(self, *args):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]).replace("/", ""))
            i += 1

        self.datatable_url = self.base_url[1:] + "/".join(tmp) + "/"

    def get_generic_link(self, *args, **kwargs):
        tmp = list()
        i = 0
        while i < len(args):
            if args[i] is not None:
                tmp.append(str(args[i]).replace("/", ""))
            i += 1

        try:
            base_url = kwargs["base_url"] + "/"
        except KeyError:
            base_url = self.base_url

        ret = base_url + "/".join(tmp) + "/"

        return ret

    @staticmethod
    def check_duplicate(queryset, pk=None, response=None):

        error = False

        try:
            c_ini = queryset.pk
            if str(c_ini) != str(pk):
                error = True
        except MultipleObjectsReturned:
            error = True
        except (TypeError, AttributeError, ObjectDoesNotExist):
            pass

        if error:
            return response
        else:
            return None