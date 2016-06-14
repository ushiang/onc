import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from packages.bin.auth import Auth
from packages.bin.base_controller import BaseController
from packages.bin.bin import Page, Table
from packages.bin.lib import response_generic, response_error, format_form_error, response_success, empty


class UsersController(BaseController):

    def dispatch(self, *args, **kwargs):

        from .models import Users

        self.model = Users

        self.base_url = "/system/users/"
        self.base_template = "system/"

        self.second_base = "users"
        self.second_base_alt = "users/"

        self.page = Page(args)
        self.page.title = _('User Management')
        self.page.icon = 'fa fa-user'
        self.page.form_name = 'userForm'
        self.page.theme = "info"
        self.page.theme_menu = "primary"
        self.page.base_template = self.base_template
        self.page.second_base = self.second_base_alt
        self.page.hide_title = True
        self.page.form = 'form.html'
        self.page.script = ""
        self.page.menu = ""
        self.page.rest_link = ""
        self.page.mode = "type"
        self.page.breadcrumbs = [
            {'link': '#/system/users/', 'label': _('User Management')},
            {'label': _('Manage Users')},
        ]

        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get(self, request, method=None, pk=None, do=None):

        self.page.method = method

        if method == "new" or method == "update":
            return self.get_manage(request, method, pk)

        elif method == "delete":
            return self.get_delete(request, pk, do)

        elif method == "reset-password":
            return self.get_reset_password(request, pk, do)

        elif method == "reset-all-password":
            return self.get_reset_all_password(request)

        elif method == "forgot-password":
            return self.get_forgot_password(request)

        elif method == "change-password":
            return self.get_change_password(request, pk)

        elif method == "status":
            return self.get_toggle_user_status(request, method, pk, do)

        elif method == "lock-session":
            return self.get_lock_account(request)

        elif method == "logout-session" or method == "logout":
            return self.get_logout(request)

        elif method == "delete":
            return self.get_delete(request, method, pk)

        else:
            return self.get_index(request)

    def post(self, request, method=None, pk=None):
        try:
            self.page.method = method

            if method == "new" or method == "update":
                return self.post_manage(request, method, pk)

            elif method == "forgot-password":
                return self.post_forgot_password(request)

            elif method == "change-password":
                return self.post_change_password(request, pk)

        except Exception:
            print traceback.print_exc()

    def get_index(self, request):

        # s = Auth().is_auth(request)
        # if not s:
        #     return Auth.routeLogin

        self.set_template("users", "index.html")
        self.set_menu("users", "menu.html")
        self.set_datatable_url("dt", "users")

        # build table
        table = Table()
        table.settings = True
        table.cols = [_("Email"), _("User Classes"), _("Profile Name"), _("Active"), _("Reset Password")]
        table.url = self.datatable_url

        return render_to_response(
            self.template,
            {'page': self.page, 'form': self.form, 'table': table},
            context_instance=RequestContext(request)
        )

    def get_manage(self, request, method=None, pk=None):

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        from .forms import FormRegister

        self.form_obj = FormRegister
        self.form = self.form_obj()

        if method == 'update':
            self.instance = self.model.pp.get(pk=pk)
            self.form = self.form_obj(instance=self.instance, data=model_to_dict(self.instance))

        else:
            self.instance = self.model()
            self.form = self.form_obj(instance=self.instance)

        self.form = self.form_obj(instance=self.instance, data=model_to_dict(self.instance))

        self.set_template("users", "manage.html")
        self.set_menu("users", "menu.html")
        self.set_form_action(method, pk)
        self.page.view = "form-users.html"
        self.page.method = method
        self.page.obj = self.instance

        return render_to_response(
            self.template,
            {'page': self.page, 'form': self.form},
            context_instance=RequestContext(request)
        )

    def get_reset_password(self, request, pk=None, do=None):

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        from packages.bin.bin import get_company

        second_base_url = ''

        try:
            obj = self.model.pp.get(pk=pk)
        except KeyError:
            return HttpResponseRedirect('#404/hack/')

        link = {'go': self.base_url+second_base_url+'reset-password/process/'+str(pk)+'/',
                'cancel': self.base_url+second_base_url}
        page = Page(request)
        page.confirmation_value = "Reset Password"

        if not do:
            page.description = 'You are about to reset <b>%s</b>\'s password. How do you want to proceed?' % obj.email
            return render_to_response(
                request.session['style'] + '/layout/snippets/delete-confirmation-modal.html',
                {'link': link, 'page': page},
                context_instance=RequestContext(request)
            )

        elif do:
            from packages.bin.email import Email

            # send mail
            company = get_company(user=obj)
            raw_password = obj.reset_password()

            data = dict()
            data['request'] = request
            data['password'] = "%s: <strong>%s</strong>" % (_("New Password"), raw_password)
            data['company'] = company
            try:
                data['logo'] = company.company_logo_raw.url
            except (AttributeError, ValueError):
                data['logo'] = None
            data['email'] = obj.email
            data['link'] = "/system/login/"
            data['title'] = _("Password Reset")
            data['info'] = \
                _("Hi <strong>%s</strong>, your password for PostPrincipal ERP Ontogeny was reset "
                  "successfully, to login please use the temporary generated password below") % \
                obj.profile.get_fullname()

            subject = _("Password Reset Confirmation - %s" % company.company_name)
            email_object = Email(
                request, to=[obj.email], subject=subject, data=data
            )
            email_object.email_template = "system/email/reset-password.html"
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            email_object.use_tls = company.use_tls
            email_object.send()

            # notify user of success
            msg = _("User password was reset successfully")
            return HttpResponse(response_success(route='/system/users/', response=msg))

    def get_reset_all_password(self, request):
        from packages.bin.bin import get_company
        from packages.bin.email import Email

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        for user_object in self.model.pp.filter(first_time=True):
            raw_password = user_object.reset_password()

            # get license object
            company = get_company(user=user_object)

            # send mail
            data = dict()
            data['request'] = request
            data['password'] = raw_password
            data['company'] = company
            try:
                data['logo'] = company.company_logo_raw.url
            except (AttributeError, ValueError):
                data['logo'] = None
            data['email'] = user_object.email
            data['link'] = "/system/login/"
            data['title'] = _("Password Reset")
            data['info'] = \
                _("Hi <strong>%s</strong>, your password for PostPrincipal ERP Ontogeny was reset "
                  "successfully, to login please use the temporary generated password below") % \
                user_object.profile.get_fullname()
            data['password'] = "%s: <strong>%s</strong>" % (_("New Password"), raw_password)

            subject = _("Password Reset Confirmation - %s" % company.company_name)

            email_object = Email(request, to=[user_object.email], subject=subject, data=data)
            email_object.email_template = "system/email/forgot-password.html"
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            # email_object.send()

        msg = _("Passwords where reset and sent to respective user")
        style = 'success'

        return HttpResponse(
            response_generic(response=msg, delay=2000, style=style)
        )

    @staticmethod
    def get_forgot_password(request):
        from .forms import FormForgotPassword

        Auth().do_logout(request, log_timeout=False)

        page = Page(request)
        template = 'forgot-password.html'

        form = FormForgotPassword()
        form.action = '/system/users/forgot-password/'
        return render_to_response(template, {'form': form, 'page': page}, context_instance=RequestContext(request))

    @staticmethod
    def get_change_password(request, pk=None):
        from packages.system.forms import FormChangePassword

        Auth().do_logout(request, log_timeout=False)

        page = Page(request)
        template = 'change-password.html'

        form = FormChangePassword()
        form.action = '/system/users/change-password/%s/' % pk
        return render_to_response(template, {'form': form, 'page': page}, context_instance=RequestContext(request))

    def get_toggle_user_status(self, request, method=None, pk=None, do=None):

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        try:
            obj = self.model.pp.get(pk=pk)
        except KeyError:
            return HttpResponseRedirect('#404/hack/')

        if method is not None and pk is not None:
            if do == 'activate':
                obj.active = 1
                msg = _("User was activated successfully")
            elif do == 'deactivate':
                obj.active = 0
                msg = _("User was deactivated successfully")
            else:
                msg = _("Command sent is not recognized")

            obj.save()

            js_command = "WitMVC_UI.resetTable();"

            return HttpResponse(
                response_generic(route='/system/users/', style="success", response=msg, command=js_command)
            )

    @staticmethod
    def get_lock_account(request):
        return Auth().do_logout(request)

    @staticmethod
    def get_logout(request):
        return Auth().do_logout_final(request)

    def get_delete(self, request, pk=None, do=False):
        from django.db.models import ProtectedError
        from .models import Users

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        self.second_base = 'users'

        self.model = Users

        try:
            instance = self.model.pp.get(pk=pk)
        except KeyError:
            return Auth.do_403()

        link = {
            'go': self.get_generic_link(self.second_base, "delete", "process", pk),
            'cancel': self.get_generic_link(self.second_base),
        }

        page = Page(request)
        page.confirmation_theme = "alert alert-dark"

        if not do:
            page.description = _('You are about to delete a user from your database <b>(%s)</b>. '
                                 'How do you want to proceed?').decode('UTF-8') % instance
            return render_to_response(request.session['style'] + '/layout/snippets/delete-confirmation.html',
                                      {'link': link, 'page': page}, context_instance=RequestContext(request))

        elif do:
            # prevents CASCADE DELETE from the model settings
            try:
                instance.delete()
                response = _("Personnel information was deleted successfully")
                style = 'info'
                route = link["cancel"]
                delay = 2000

            except ProtectedError:
                response = _("Cannot delete user, because other data keys are associated to these user "
                             "like organization information, hr_leave logs, training logs e.t.c.<br/>"
                             "However you can deactivate this user by clicking %s") % \
                           "<a ui-WitMVC-href href='#/system/user/deactivate/%s/'>%s</a>" % \
                           (instance.pk, _("here"))
                style = 'danger'
                delay = 15000
                route = None

            return HttpResponse(response_generic(route=route, response=response, delay=delay, style=style))

    def post_manage(self, request, method=None, pk=None):

        from .forms import FormRegister

        s = Auth().is_auth(request)
        if not s:
            return Auth.routeLogin

        self.form_obj = FormRegister
        errors = list()

        if method == 'update':
            self.instance = self.model.pp.get(pk=pk)
            self.form = self.form_obj(instance=self.instance, data=model_to_dict(self.instance))

        elif method == 'new':
            self.instance = self.old_instance = self.model()
            self.form = self.form_obj(instance=self.instance)

        # clean up data
        self.form = self.form_obj(request.POST, instance=self.instance)

        if self.form.is_valid():
            # do method to process
            for post in request.POST:
                # skip the many to many fields
                if hasattr(self.instance, post):
                    setattr(self.instance, post, self.form.cleaned_data[post])

            # check for duplicates
            try:
                queryset = self.model.pp.get(email__iexact=self.instance.email)
                msg = _("The email you have selected is unavailable")
                duplicate = self.check_duplicate(queryset=queryset, pk=pk, response=msg)
                errors.append(duplicate) if duplicate else True
            except ObjectDoesNotExist:
                pass
            except Exception:
                print traceback.print_exc()
                errors.append("Some unknown errors occurred")

        # do some non field specific validations
        try:
            del self.form.errors['profile']
        except KeyError:
            pass

        if empty(self.instance.firstname) and empty(self.instance.lastname):
            errors.append(_("You must enter firstname and lastname of the user"))

        errors += format_form_error(self.form)
        # errors.append("Debugging")

        if not errors:
            from hashlib import sha1
            from packages.bin.bin import get_company, Email
            from packages.hr.hr_personnel.models import Basic
            from packages.hr.hr_organization.models import Organization

            raw_password = ""

            if pk is None:
                basic, c = \
                    Basic.pp.get_or_create(reference=self.instance.email, firstname=self.instance.firstname,
                                           lastname=self.instance.lastname, email=self.instance.email,
                                           defaults={
                                               "c_status": -1
                                           })

                # check if password is empty
                from packages.bin.lib import random_chars
                raw_password = next(random_chars(8))

            else:
                basic = Basic.pp.get(pk=self.instance.profile.id)
                basic.reference = basic.reference or self.instance.username
                basic.firstname = self.instance.firstname
                basic.lastname = self.instance.lastname
                basic.email = self.instance.email

            basic.save()

            # add organization info if not exists
            Organization.pp.get_or_create(profile=basic)

            self.instance.profile = basic
            self.instance.username = self.instance.email
            if pk is None:
                self.instance.password = sha1(raw_password).hexdigest()
            self.instance.save()

            # notify user of success
            msg = _("User was created successfully")
            return HttpResponse(response_success(route='/system/users/', response=msg))

        else:
            return HttpResponse(response_error(response=[errors]))

    def post_change_password(self, request, pk=None):

        from hashlib import sha1
        from packages.bin.bin import get_company
        from packages.system.forms import FormChangePassword

        error = list()

        page = Page(request)
        template = 'change-password.html'

        form = FormChangePassword()
        form.action = '/system/users/change-password/%s/' % pk

        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # check if a user object is active
        if pk is None:
            error.append(_("An internal error occurred, please try again"))

        # check if old password is consistent with user object
        try:
            user_object = self.model.objects.get(pk=pk, password=sha1(old_password).hexdigest())
        except self.model.DoesNotExist:
            error.append(_("User object not found for credentials given"))
            user_object = None

        # check for consistency in confirm-password and new-password
        if new_password != confirm_password:
            error.append(_("New password is not consistent with confirm password"))

        # check for password strength
        from packages.bin.lib import password_checker
        password_score, password_error = password_checker(new_password, 4, ['password', old_password])
        if password_score is not True:
            if password_error is not None:
                error.append(password_error)
            else:
                error.append(_("Your password should contain, one lowercase, an uppercase and a number, and "
                               "should be between 6 to 12 characters long"))

        error = "<br />".join(error)

        if not error:

            from packages.bin.email import Email

            user_object.first_time = False
            user_object.password = sha1(new_password).hexdigest()
            user_object.alt_save()

            # get license object
            company = get_company(user=user_object)

            # send mail
            data = dict()
            data['request'] = request
            data['company'] = company
            try:
                data['logo'] = company.company_logo_raw.url
            except (AttributeError, ValueError):
                data['logo'] = ""
            data['email'] = user_object.email
            data['link'] = "/system/login/"
            data['title'] = _("Password Changed Successfully")
            data['info'] = \
                _("Hi <strong>%s</strong>, your password for PostPrincipal ERP Ontogeny was changed "
                  "successfully. Please click on the button below to login") % \
                user_object.profile.get_fullname()

            subject = _("Password Changed Successfully - %s" % company.company_name)

            email_object = Email(request, to=[user_object.email], subject=subject, data=data)
            email_object.email_template = "system/email/change-password.html"
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            email_object.use_tls = company.use_tls
            email_object.send()

            return HttpResponseRedirect('/system/login/?_logout=1')

        return render_to_response(
            template,
            {'form': form, 'page': page, 'formError': error},
            context_instance=RequestContext(request)
        )

    def post_forgot_password(self, request):

        from packages.bin.bin import get_company
        from .forms import FormForgotPassword

        error = list()

        page = Page(request)
        template = 'forgot-password.html'

        form = FormForgotPassword()
        form.action = '/system/users/forgot-password/'

        email = request.POST['email']

        # check if old password is consistent with user object
        try:
            user_object = self.model.objects.get(email=email)

        except self.model.DoesNotExist:
            error.append(_("The email you entered wasn't found on our database"))
            user_object = None

        error = "<br />".join(error)

        if not error:

            from packages.bin.email import Email

            raw_password = user_object.reset_password()

            # get license object
            company = get_company(user=user_object)

            # send mail
            data = dict()
            data['request'] = request
            data['password'] = raw_password
            data['company'] = company
            try:
                data['logo'] = company.company_logo_raw.url
            except (AttributeError, ValueError):
                data['logo'] = ""
            data['email'] = user_object.email
            data['link'] = "/system/login/"
            data['title'] = _("Password Reset")
            data['info'] = \
                _("Hi <strong>%s</strong>, your password for PostPrincipal ERP Ontogeny was reset "
                  "successfully, to login please use the temporary generated password below") % \
                user_object.profile.get_fullname()
            data['password'] = "%s: <strong>%s</strong>" % (_("New Password"), raw_password)

            subject = _("Password Reset Confirmation - %s" % company.company_name)

            email_object = Email(request, to=[user_object.email], subject=subject, data=data)
            email_object.email_template = "system/email/forgot-password.html"
            email_object.auth_email = company.auth_email
            email_object.auth_password = company.auth_password
            email_object.smtp_host = company.smtp_host
            email_object.smtp_port = company.smtp_port
            email_object.use_tls = company.use_tls
            email_object.send()

            # return email_object.preview()

            return HttpResponseRedirect('/system/login/?_logout=1')

        return render_to_response(
            template,
            {'form': form, 'page': page, 'formError': error},
            context_instance=RequestContext(request)
        )
