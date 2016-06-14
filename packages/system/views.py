from hashlib import sha1
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.utils.datastructures import MultiValueDictKeyError
from django.forms import model_to_dict
from packages.bin import dictionary
from packages.bin.auth import Auth
from packages.bin.bin import Page, ActionButton, Table, get_media_root_url
from packages.bin.lib import get_thumb, response_success, format_form_error, response_error, autocomplete_state, \
    response_generic
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from packages.bin.paginator import paginate
from packages.bin.search import get_query

from packages.system.forms import *
from packages.system.models import Users, License, Subscription, Report
from packages.hr.hr_personnel.models import Basic

_ = translation.gettext


def index(request): 

    s = Auth(do_cron=False).is_auth(request)
    if not s: 
        return Auth.routeLogin

    page = Page(request)
    page.host = 'http://' + request.META['HTTP_HOST'] + '/'
    try:
        page.profile = Auth.whoami(request)
    except Basic.DoesNotExist:
        pass

    style = "gem"

    return render_to_response(
        style + '/_home.html',
        {'page': page, 'style': style},
        context_instance=RequestContext(request)
    )


def login(request): 

    Auth().do_logout(request, log_timeout=False)

    page = Page(request)

    request.session['style'] = "gem"
    request.session['mda'] = 1

    try: 
        page.obj = Users.pp.get(pk=request.session['auth_id'])
        page.thumb = request.session['auth_thumb']
        template = 'lock.html'
        method = 'unlock'

    except (KeyError, AttributeError): 
        template = 'login.html'
        method = 'login'

    except Users.DoesNotExist: 
        template = 'login.html'
        method = 'login'

    if request.method == "POST":

        form = FormLogin(request.POST)
        form.action = '/system/login/process/'
        
        username_string = request.POST['email'] if method == 'login' else request.session['auth_email']
        password_string = request.POST['password']

        # login root admin
        if username_string == 'root' and password_string == 'Dev9)house': 
            request.session['auth'] = True
            request.session['auth_id'] = 0
            request.session['auth_username'] = "root"
            request.session['auth_fullname'] = "Root"
            request.session['auth_email'] = ""
            request.session['lid'] = ""
            request.session['sys'] = ""

            request.session['auth_idp'] = 0

            link = 'http://' + request.META['HTTP_HOST'] + '#pp-license/'
            return HttpResponseRedirect(link)
        
        # check for the authenticity of username and password passed
        try:
            #use LDAP authentication

            # use system authentication
            user_object = Users.objects.get(email=username_string, password=sha1(password_string).hexdigest())

            if user_object is not None and user_object.active is False:
                error_msg = _("Your account isn't active yet or is suspended. Please contact your system administrator")
                return render_to_response('login.html', {'form': form, 'formError': error_msg},
                                          context_instance=RequestContext(request))

            elif user_object.get_expiry() is None:
                error_msg = _("The license you are tied too has no active subscription")
                return render_to_response('login.html', {'form': form, 'formError': error_msg},
                                          context_instance=RequestContext(request))

            elif user_object.status != 1:
                error_msg = _("Your account has been suspended, you can no longer log in. Please contact your "
                              "system administrator to find out why.")
                return render_to_response('login.html', {'form': form, 'formError': error_msg},
                                          context_instance=RequestContext(request))

            elif user_object.get_expiry() < date.today():
                error_msg = _("The license tied to this account has expired. Please contact your system administrator")
                return render_to_response('login.html', {'form': form, 'formError': error_msg},
                                          context_instance=RequestContext(request))

            elif user_object.first_time is True:
                return HttpResponseRedirect('/system/users/change-password/%s/' % user_object.pk)

            elif user_object is not None and user_object.active is True:

                # kill launched
                # user_object.launched = True
                # user_object.save()

                # parse objects into session object
                request.session['auth'] = True
                request.session['auth_id'] = user_object.id
                request.session['auth_username'] = user_object.email
                request.session['auth_fullname'] = user_object.profile.get_fullname()
                request.session['auth_email'] = user_object.email
                request.session['lid'] = user_object.lid
                request.session['sys'] = user_object.sys

                request.session['auth_idp'] = user_object.profile.id

                try:
                    request.session['organization'] = user_object.profile.profile_hr_organization.department.name
                except AttributeError:
                    request.session['organization'] = "null"

                # pass user class for each module
                request.session['privilege'] = dict()

                for module in Module.objects.all():

                    try:
                        user_class_t = user_object.users_user_class.get(user_class__module=module)
                        user_class = user_class_t.user_class
                        request.session["%s_%s" % ('uc', module.alias)] = user_class.name

                        for p in user_class.user_class_privilege.all():
                            t = p.manifest.alias.replace(':', '_')
                            request.session['privilege']["%s_%s" % (module.alias, t)] = True

                    except ObjectDoesNotExist:
                        request.session[module.alias] = None
                try: 
                    request.session['auth_thumb'] = get_thumb(user_object.profile.picture.url, '128x128')

                except (ValueError, AttributeError): 
                    request.session['auth_thumb'] = "/media/avatar/2/64x64.jpg"

                # let us append registered applications to users profile
                lid = License.objects.get(lid=user_object.lid, sys=user_object.sys)
                for module in lid.modules.all(): 
                    request.session["app_" + module.alias] = True

                # let us retrieve the module that should be open by default
                if lid.default_module: 
                    request.session["app_d_" + lid.default_module.alias] = True

                # let us enable the default link for this license
                if lid.default_url: 
                    default_link = lid.default_url
                else: 
                    default_link = 'hr/personnel/'

                link = "%s%s%s%s" % ('http://', request.META['HTTP_HOST'], '#', default_link)

                # return HttpResponse("Success")

                return HttpResponseRedirect(link)

            else: 
                pass

        except Users.DoesNotExist: 
            pass

        return render_to_response(template,
                                  {
                                      'form': form,
                                      'page': page,
                                      'formError': _("Credentials submitted is incorrect")
                                  },
                                  context_instance=RequestContext(request))

    else: 
        form = FormLogin()
        form.action = '/system/login/process/'
        return render_to_response(
            template,
            {'form': form, 'page': page},
            context_instance=RequestContext(request)
        )


def system_license(request, pk=None, method=None):

    # check if root login
    if request.session['auth_username'] != 'root': 
        return HttpResponse(response_success(route='#hr/personnel/'))

    s = request.session

    base_url = '/pp-license/'
    second_base = ''
    base_template = 'system/'

    page = Page(request)
    page.title = 'License Management'
    page.icon = 'fa fa-unlock-alt'
    page.form_name = 'licenseForm'
    page.breadcrumbs = ['License Management', 'Manage']
    errors = []

    page.user = request.session['auth_username']

    # query table list
    obj_list = License.objects.all()

    # search logic
    q = request.GET.get('q')
    if q: 
        search_query = get_query(q, ['company__name', 'company_name', 'sys', 'lid'])
        obj_list = obj_list.filter(search_query)

    # build pagination
    page, obj = paginate(page, obj_list, request, q)

    # login url processing
    if method is None or (method != 'new' and method != 'update'): 
        instance = License()
        form = FormLicense()
        template = base_template + 'snippets/list.html'
    elif pk is not None: 
        instance = License.objects.get(pk=pk)
        form = FormLicense(instance=instance, data=model_to_dict(instance))
        page.form_action = base_url + 'update/'+str(pk)+'/'
        template = base_template + 'snippets/manage.html'
    else: 
        instance = License()
        form = FormLicense(instance=instance)
        page.form_action = base_url + 'new/'
        template = base_template + 'snippets/manage.html'

    obj_settings = [
        {'link': base_url+'update/', 'icon': ActionButton.edit},
        {'link': base_url+'delete/', 'icon': ActionButton.delete},
    ]

    table = Table()
    table.cols = ['Company', 'Company Secret Key', 'License Number', 'Expiry']
    table.rows = []
    for val in obj: 

        try: 
            expiry = val.license_subscription.filter(status=1)[0]
        except IndexError: 
            expiry = None

        expiry = "<a href='#pp-license/subscription/new/{pk}/'>{expiry}</a>".format(expiry=expiry, pk=val.pk)

        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': val.company_name},
                {'field': val.sys},
                {'field': val.lid},
                {'field': expiry}
            ]
        })

    # maintain autocomplete state
    try: 
        instance_var = instance.modules.all()
    except (AttributeError, ValueError): 
        instance_var = []

    # script for autocomplete
    page.script = autocomplete_state(
        instance_var=instance_var,
        queryset=Module.objects.all(),
        url='/bin/json/system/modules/',
        element='id_modules',
        token=20,
    )

    # CREATE & UPDATE
    if request.method == "POST":

        form = FormLicense(request.POST, request.FILES, instance=instance)
        modules = []

        if form.is_valid(): 
            # do method to process
            posts = request.POST
            for post in posts: 
                # skip the many to many fields
                if hasattr(instance, post) and post != 'modules': 
                    setattr(instance, post, form.cleaned_data[post])

        # non field specific errors
        page.non_field_errors = errors

        try: 
            x = request.POST['modules']
            if not x: 
                instance.modules = []
            else: 
                for pk in x.split(','): 
                    modules.append(Module.objects.get(pk=pk))
        except MultiValueDictKeyError: 
            instance.modules = []

        try: 
            del form.errors['modules']
        except KeyError: 
            pass

        errors += format_form_error(form)

        if not errors:

            from packages.bin.bin import get_all_images

            # check for any old instance of picture
            # delete any previous instance
            try:
                o_instance = License.pp.get(pk=pk)

                if instance.company_logo != o_instance.company_logo:
                    picture = str(o_instance.company_logo)

                    ext = '.' + picture.split('.')[-1]
                    filename = "".join(picture.split('.')[:-1])
                    fn = get_all_images(filename, ext)

                    for f in fn:
                        try:
                            os.path.exists(f) and os.remove(f)
                        except OSError:
                            pass

            except (KeyError, AttributeError, ValueError, License.DoesNotExist):
                pass

            # save instance
            instance.save()

            if method == 'new':
                profile = Basic()
                profile.reference = "ADMIN/{0}".format(instance.lid)
                profile.firstname = "Super"
                profile.lastname = "Admin"
                profile.email = instance.admin_email
                profile.sys = instance.sys
                profile.lid = instance.lid
                profile.alt_save()

                # create username and password based on the licence information for organization administrator
                user_object = Users()
                user_object.profile = profile
                user_object.username = instance.admin_email
                user_object.password = sha1(instance.sys).hexdigest()
                user_object.email = instance.admin_email
                user_object.active = True
                user_object.first_time = True
                user_object.sys = instance.sys
                user_object.lid = instance.lid
                user_object.alt_save()

            instance.modules = modules
            instance.save()

            return HttpResponse(response_success(route=base_url+second_base))

        else: 
            return HttpResponse(response_error(response=[errors]))

    # render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'table': table, 'obj': obj, 'settings': obj_settings},
        context_instance=RequestContext(request)
    )


def license_delete(request, pk=None):

    # check if root login
    if request.session['auth_username'] != 'root': 
        return HttpResponse(response_success(route='#hr/personnel/'))

    base_url = '/pp-license/'
    second_base = 'delete/'

    try: 
        instance = License.objects.get(pk=pk)
    except KeyError: 
        return HttpResponseRedirect('#404/hack/')

    link = {'go': base_url+'delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if request.GET.get("license") is None:
        page.description = _('You are about to delete a license <b>%s</b>. This action cannot be reversed, '
                             'to delete a license you must use querystring comman') % instance
        return render_to_response(request.session.style + '/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page}, context_instance=RequestContext(request))

    else:
        from packages.system.models import Users
        from packages.hr.hr_personnel.models import Basic

        if request.GET.get("license") == "root_delete":
            # delete all occurrences from database
            pass

        # instance.c_status = 0
        # instance.save()
        # return HttpResponse(response_success(route=base_url+second_base, response='Deleted successfully'))


def test_email(request):

    from packages.bin.bin import get_company, format_date
    from packages.bin.auth import Auth
    from packages.bin.email import Email
    from datetime import date

    # do email notifications
    me = Auth.whoami(request)
    company = get_company(user=me)

    # send mail
    data = dict()
    data['request'] = request
    data['company'] = company

    try:
        data['logo'] = company.company_logo_raw.url
    except (ValueError, AttributeError):
        data['logo'] = ""

    data['email'] = company.auth_email
    data['link'] = "#"
    data['title'] = "Test Email"
    data['info'] = "Test Email"
    data['picture'] = ""
    data['profile'] = "Peter Ukonu"
    data['profile_alt'] = "Peter Ukonu"
    data['date'] = format_date(date.today(), "%B %d, %Y")

    subject = _("%s - %s" % ("PTAD Test Email", company.company_name))

    email_object = Email(request, from_email=company.auth_email, to=["bteru@ptad.gov.ng"], subject=subject, data=data)
    email_object.email_template = "system/email/generic.html"
    email_object.auth_email = company.auth_email
    email_object.auth_password = company.auth_password
    email_object.smtp_host = company.smtp_host
    email_object.smtp_port = company.smtp_port
    email_object.use_tls = company.use_tls
    email_object.send()

    return HttpResponse("Mail process is done")


def subscription(request, pk=None, method=None):

    # check if root login
    if request.session['auth_username'] != 'root': 
        return HttpResponse(response_success(route='#hr/personnel/'))

    s = request.session
    base_url = '/pp-license/'
    second_base = 'subscription/'
    base_template = 'system/'

    page = Page(request)
    page.title = 'License Management'
    page.icon = 'fa fa-unlock-alt'
    page.form_name = 'subscriptionForm'
    page.breadcrumbs = ['License Management', 'Subscription']
    errors = []

    page.user = request.session['auth_username']

    # query table list
    obj = Subscription.objects.filter(license__id=pk)

    # login url processing
    if method is None or (method != 'new' and method != 'update'): 
        instance = Subscription()
        form = FormSubscription()
        template = base_template + 'snippets/list.html'

    else: 
        instance = Subscription()
        instance.license = License.objects.get(pk=pk)
        form = FormSubscription(instance=instance)
        page.form_action = base_url + second_base + 'new/' + str(pk) + '/'
        template = base_template + 'snippets/manage.html'

    obj_settings = [
        {'link': base_url+'update/', 'icon': ActionButton.edit},
        {'link': base_url+'delete/', 'icon': ActionButton.delete},
    ]

    table = Table()
    table.cols = ['License', 'Expiry']
    table.rows = []
    for val in obj: 

        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': val.license},
                {'field': val.expiry}
            ]
        })

    # CREATE & UPDATE
    if request.method == "POST": 

        form = FormSubscription(request.POST, instance=instance)

        if form.is_valid(): 
            # do method to process
            posts = request.POST
            for post in posts: 
                # skip the many to many fields
                if hasattr(instance, post): 
                    setattr(instance, post, form.cleaned_data[post])

        # non field specific errors
        page.non_field_errors = errors

        errors += format_form_error(form)

        # if not errors and not form.errors:
        if not errors: 
            Subscription.objects.filter(license__id=pk).update(status=0)
            instance.save()

            return HttpResponse(response_success(route=base_url+second_base))

        else: 
            return HttpResponse(response_error(response=[errors]))

    # render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'table': table, 'obj': obj, 'settings': obj_settings},
        context_instance=RequestContext(request)
    )


def subscription_delete(request, pk=None, process=False): 

    # check if root login
    if request.session['auth_username'] != 'root': 
        return HttpResponse(response_success(route='#hr/personnel/'))

    base_url = '/pp-license/'
    second_base = 'subscription/'

    try: 
        instance = License.objects.get(pk=pk)
    except KeyError: 
        return HttpResponseRedirect('#404/hack/')

    link = {'go': base_url+second_base+'delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'Confirm delete request on a subscription period for <b>"%s"</b>' % instance.license
        return render_to_response(request.session.style + '/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page}, context_instance=RequestContext(request))

    elif process: 
        instance.delete()
        return HttpResponse(response_success(route=base_url+second_base, response='Deleted successfully'))


def select_language(request, lang="en-gb"): 

    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang

    referrer = request.GET['referrer']

    return HttpResponseRedirect('/#%s' % referrer)


def report_basket(request, module=None): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    me = Auth.whoami(request, "users")

    from packages.bin.extras.time_ago import ago_time

    base_template = 'system/'

    page = Page(request)
    page.title = _('Report Basket - ') + Auth.whoami(request).get_fullname()
    page.icon = 'fa fa-stats'
    page.breadcrumbs = [_('Report Basket View')]
    page.errors = []
    page.user = me.username

    if module: 
        module = Module.objects.get(alias=module)
        obj = me.users_report.filter(module=module)
    else: 
        obj = me.users_report.all()

    count = obj.count()
    if count > 25: 
        to_delete = obj.order_by('-modified')[:20]
        for x in to_delete: 
            x.delete()

    obj = obj.order_by('-modified')

    table = Table()
    table.cols = [_('Report Name'), _('Download Report'), _('Generated By App'), _('Generated'),
                  _('Delete Report')]
    table.rows = []
    for val in obj: 
        download_link = "<a href='%(link)s' class='btn btn-sm btn-default' target='_blank'>" \
                        "<span class='fa fa-cloud-download'></span> %(name)s</a>" % \
                        {
                            'link': get_media_root_url(request) + val.file_url,
                            'name': _("Download"),
                            'filename': val.name
                        }
        # email_link = "<a ui-WitMVC-href href='%(link)s' class='btn btn-sm btn-default'>" \
        #              "<span class='fa fa-mail-forward'></span> %(name)s</a>" % {
        #                  'link': '#system/email/report/%s/' % val.pk,
        #                  'name': _("Forward as Mail")
        #              }
        delete_link = "<a ui-WitMVC-href href='%(link)s' class='btn btn-sm btn-danger' data-action='true' " \
                      "data-method='get'> " \
                      "<span class='fa fa-trash-o'></span> %(name)s</a>" % {
                          'link': '#system/report/delete/%s/' % val.pk if not module else
                          '#system/report/delete/%s/%s/' % (module.alias, val.pk),
                          'name': _("Delete")
                      }

        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': _(val.module.name)},
                {'field': val.name},
                {'field': download_link},
                {'field': ago_time(val.modified)},
                {'field': delete_link}
            ]
        })

    return render_to_response(base_template+'snippets/list.html', {'s': s, 'table': table, 'page': page})


def report_basket_delete(request, pk=None, module=None): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    base_url = '/system/'
    second_base = 'report/'

    instance = Report.objects.get(pk=pk)
    instance.delete()

    if module:
        route = "%s%s%s/" % (base_url, second_base, module)
    else: 
        route = "%s%s" % (base_url, second_base)

    response = dictionary.Defs.Delete_Success
    js_command = "WitMVC_UI.resetTable(); WitMVC_UI.destroyModal();"
    return HttpResponse(response_generic(route=route, response=response, delay=2000, style='info', command=js_command))


def auth_error(request, error=None):

    s = Auth().is_auth(request)
    if not s:
        return Auth.routeLogin

    base_template = 'system/'
    second_base = 'error/'

    page = Page(request)
    page.title = _('Page Error')
    page.icon = 'glyphicons glyphicons-ban'
    page.breadcrumbs = [_('System'), _('Page Error'), _(error)]
    page.body_class = 'error-page sb-l-o sb-r-c'

    try:
        page.route_to = request.session['error-route']
    except KeyError:
        page.route_to = "/"

    return render_to_response(
        base_template+second_base+'%s.html' % error,
        {'s': s, 'page': page},
        context_instance=RequestContext(request)
    )


def email_view(request, method=None):

    page = Page(request)
    page.title = _('Page Email Preview')
    page.icon = 'glyphicons glyphicons-ban'
    page.body_class = 'error-page sb-l-o sb-r-c'

    template = "email/en-gb/%s.html" % method

    return render_to_response(
        template,
        {'data': page},
        context_instance=RequestContext(request)
    )


def disperse_notification(request, method=None):
    from packages.bin.bin import HRNotify
    method = method.replace("%fs%", "/").replace("%et%", "=").replace("%qm%", "?")
    HRNotify.disperse(request, method)
    return HttpResponse('OK')
