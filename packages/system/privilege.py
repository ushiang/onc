from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.template import RequestContext
from django.utils.translation import gettext as _
from packages.bin.auth import Auth
from packages.bin.bin import Page, Table, ActionButton
from packages.bin.lib import response_success, response_error, format_form_error
from packages.bin.search import get_query
from packages.bin.paginator import paginate
from packages.system import forms
from packages.system.models import *

base_url = '/system/privilege/'
base_template = 'system/privilege/'


def module(request, pk=None, method=None): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'module/'

    page = Page(request)
    page.title = 'Application Modules'
    page.icon = 'glyphicons glyphicons-claw_hammer'
    page.form_name = 'applicationModules'
    page.breadcrumbs = ['Privileges', 'Applications', 'Modules']
    errors = []

    obj_list = Module.objects.filter(status__exact=1)

    #search logic
    q = request.GET.get('q')
    if q: 
        search_query = get_query(q, ['name'])
        obj_list = obj_list.filter(search_query)

    #build pagination
    page, obj = paginate(page, obj_list, request, q)

    #login url processing
    if method is None or method == 'index': 
        instance = Module()
        form = forms.FormModule()
        template = base_template + 'list.html'
    elif pk is not None: 
        instance = Module.objects.get(pk=pk)
        form = forms.FormModule(instance=instance, data=model_to_dict(instance))
        page.form_action = base_url + second_base + 'update/'+str(pk)+'/'
        template = base_template + 'manage.html'
    else: 
        instance = Module()
        form = forms.FormModule(instance=instance)
        page.form_action = base_url + second_base + 'new/'
        template = base_template + 'manage.html'

    obj_settings = [
        {'link': base_url+second_base+'update/', 'icon': ActionButton.edit},
        {'link': base_url+'module-delete/', 'icon': ActionButton.delete},
    ]

    table = Table()
    table.cols = ['Name', 'Author', 'Version']
    table.rows = []
    for val in obj: 
        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': val.name},
                {'field': val.author},
                {'field': val.version}
            ]
        })

    # CREATE & UPDATE
    if request.method == "POST": 

        form = forms.FormModule(request.POST, instance=instance)
        if form.is_valid(): 
            #do method to process
            posts = request.POST
            for post in posts: 
                if hasattr(instance, post): 
                    setattr(instance, post, form.cleaned_data[post])

        # non field specific errors
        page.non_field_errors = errors

        errors += format_form_error(form)

        if not errors: 
            instance.save()
            response = 'Saved successfully'
            return HttpResponse(response_success(route=base_url + second_base, response=response))

        else: 
            return HttpResponse(response_error(response=[errors]))

    #render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'table': table, 'obj': obj, 'settings': obj_settings},
        context_instance=RequestContext(request)
    )


def module_delete(request, pk=None, process=False): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'module/'

    try: 
        instance = Module.objects.get(pk=pk)
    except KeyError: 
        return Auth.do_403()

    link = {'go': base_url + 'module-delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'You are about to delete an application module <b>[%s]</b>. How do you want to proceed?' \
                           % instance.name
        return render_to_response(request.session["style"]+'/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page},
                                  context_instance=RequestContext(request)
                                  )

    elif process:
        instance.delete()
        return HttpResponse(response_success(route=base_url+second_base, response='Deleted successfully'))


def user_class(request, pk=None, method=None):

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'user_class/'

    page = Page(request)
    page.title = 'User Class'
    page.icon = 'glyphicons glyphicons-parents'
    page.form_name = 'applicationUserClass'
    page.breadcrumbs = ['Privileges', 'User Class']
    errors = []

    obj_list = UserClass.objects.filter(status__exact=1)

    #search logic
    q = request.GET.get('q')
    if q: 
        search_query = get_query(q, ['name'])
        obj_list = obj_list.filter(search_query)

    #build pagination
    page, obj = paginate(page, obj_list, request, q)

    #login url processing
    if method is None or method == 'index': 
        instance = UserClass()
        form = forms.FormUserClass()
        template = base_template + 'list.html'
    elif pk is not None: 
        instance = UserClass.objects.get(pk=pk)
        form = forms.FormUserClass(instance=instance, data=model_to_dict(instance))
        page.form_action = base_url + second_base + 'update/'+str(pk)+'/'
        template = base_template + 'manage.html'
    else: 
        instance = UserClass()
        form = forms.FormUserClass(instance=instance)
        page.form_action = base_url + second_base + 'new/'
        template = base_template + 'manage.html'

    obj_settings = [
        {'link': base_url+second_base+'update/', 'icon': ActionButton.edit},
        {'link': base_url+'user_class-delete/', 'icon': ActionButton.delete},
    ]

    table = Table()
    table.cols = ['Module', 'Name', 'Privilege', 'Users']
    table.rows = []
    for val in obj: 

        # fetch privileges
        tmp = val.user_class_users.filter(sys=request.session['sys'], lid=request.session['lid'])[: 25]
        assoc_users = ""
        for x in tmp: 
            assoc_users += "<a href='#"+base_url+"uc_user-delete/%s/' class='text-danger'>%s</a>, " % \
                           (x.id, "%s [%s %s]" % (x.user.username, x.user.profile.firstname, x.user.profile.lastname))

        # fetch associated users
        tmp = val.user_class_privilege.all()
        assoc = ""
        for x in tmp: 
            assoc += "<a href='#"+base_url+"flush/%s/' class='text-danger'>%s</a><br/>" % (x.id, x.manifest.name)

        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': val.module.name},
                {'field': val.name},
                {'field': assoc},
                {'field': assoc_users}
            ]
        })

    # CREATE & UPDATE
    if request.method == "POST": 

        form = forms.FormUserClass(request.POST, instance=instance)
        if form.is_valid(): 
            #do method to process
            posts = request.POST
            for post in posts: 
                if hasattr(instance, post): 
                    setattr(instance, post, form.cleaned_data[post])

        # non field specific errors
        page.non_field_errors = errors

        errors += format_form_error(form)

        if not errors: 
            instance.save()
            response = 'Saved successfully'
            return HttpResponse(response_success(route=base_url + second_base, response=response))

        else: 
            return HttpResponse(response_error(response=[errors]))

    #render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'table': table, 'obj': obj, 'settings': obj_settings},
        context_instance=RequestContext(request)
    )


def user_class_delete(request, pk=None, process=False): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'user_class/'

    try: 
        instance = Module.objects.get(pk=pk)
    except KeyError: 
        return Auth.do_403()

    link = {'go': base_url + 'user_class-delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'You are about to delete a user class from %s module <b>[%s]</b>. ' \
                           'How do you want to proceed?' % (instance.module.name, instance.name)
        return render_to_response(request.session["style"]+'/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page},
                                  context_instance=RequestContext(request)
                                  )

    elif process: 
        """Check if there a users associated with this user class"""
        item_count = instance.module_privilege_manifest.all().count()
        print item_count

        if item_count > 0: 
            return HttpResponse(response_error(response="To delete this module you must first delete all privilege "
                                                        "manifest associated with it."))
        else:
            #instance.delete()
            return HttpResponse(response_success(route=base_url+second_base, response='Deleted successfully'))


def manifest(request, pk=None, method=None): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'manifest/'

    page = Page(request)
    page.title = 'Privilege Manifest'
    page.icon = 'fa fa-list-alt'
    page.form_name = 'privilegeManifest'
    page.breadcrumbs = ['Privileges', 'Manifest']
    errors = []

    obj_list = PrivilegeManifest.objects.filter(status__exact=1).order_by('module__name', 'name')

    #search logic
    q = request.GET.get('q')
    if q: 
        search_query = get_query(q, ['name'])
        obj_list = obj_list.filter(search_query)

    #build pagination
    page, obj = paginate(page, obj_list, request, q)

    #login url processing
    if method is None or method == 'index':
        instance = PrivilegeManifest()
        form = forms.FormUserClass()
        template = base_template + 'list.html'
    elif pk is not None: 
        instance = PrivilegeManifest.objects.get(pk=pk)
        form = forms.FormPrivilegeManifest(instance=instance, data=model_to_dict(instance))
        page.form_action = base_url + second_base + 'update/'+str(pk)+'/'
        template = base_template + 'manage.html'
    else: 
        instance = PrivilegeManifest()
        form = forms.FormPrivilegeManifest(instance=instance)
        page.form_action = base_url + second_base + 'new/'
        template = base_template + 'manage.html'

    obj_settings = [
        {'link': base_url+second_base+'update/', 'icon': ActionButton.edit},
        {'link': base_url+'manifest-delete/', 'icon': ActionButton.delete},
    ]

    table = Table()
    table.cols = ['Module', 'Name', 'Associated User Classes']
    table.rows = []
    for val in obj: 
        tmp = val.manifest_privilege.all()
        assoc = ""
        for x in tmp: 
            assoc += "%s<br/>" % x.user_class.name
        table.rows.append({
            'id': val.id,
            'fields': [
                {'field': val.module.name},
                {'field': val.name},
                {'field': assoc}
            ]
        })

    # CREATE & UPDATE
    if request.method == "POST": 

        form = forms.FormPrivilegeManifest(request.POST, instance=instance)
        if form.is_valid(): 
            #do method to process
            posts = request.POST
            for post in posts: 
                if hasattr(instance, post): 
                    setattr(instance, post, form.cleaned_data[post])

        # non field specific errors
        page.non_field_errors = errors

        errors += format_form_error(form)

        if not errors: 
            instance.save()
            response = 'Saved successfully'
            return HttpResponse(response_success(route=base_url + second_base, response=response))

        else: 
            return HttpResponse(response_error(response=[errors]))

    #render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'table': table, 'obj': obj, 'settings': obj_settings},
        context_instance=RequestContext(request)
    )


def manifest_delete(request, pk=None, process=False): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'manifest/'

    try: 
        instance = PrivilegeManifest.objects.get(pk=pk)
    except KeyError: 
        return Auth.do_403()

    link = {'go': base_url + 'manifest-delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'You are about to delete a user class from %s module <b>[%s]</b>. ' \
                           'How do you want to proceed?' % (instance.module.name, instance.name)
        return render_to_response(request.session["style"]+'/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page},
                                  context_instance=RequestContext(request)
                                  )

    elif process: 
        """Check if there a privileges associated with this manifest"""
        item_count = instance.manifest_privilege.all().count()
        print item_count

        if item_count > 0: 
            return HttpResponse(response_error(response="You need to delete all associated privileges before deleting "
                                                        "privilege manifest."))
        else: 
            instance.delete()
            return HttpResponse(response_success(route=base_url+second_base, response='Deleted successfully'))


def ucp(request):

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = ''

    page = Page(request)
    page.title = 'Privileges'
    page.icon = 'fa fa-list-alt'
    page.form_name = 'privilegeManager'
    page.breadcrumbs = ['Privileges']
    obj = Privilege.pp.filter(status__exact=1)

    #url processing
    instance = Privilege()
    form = forms.FormPrivilege(instance=instance)
    page.form_action = base_url + second_base + 'new/'
    template = base_template + 'manage.html'

    #script for form
    page.script = '''
    <script>

    $(document).ready(function(){
        $('#id_user_class').tokenInput('/bin/json/system/privilege/user_class/',
            {theme: 'wit', tokenLimit: 100, hintText: 'Start typing name'});
        $('#id_manifest').tokenInput('/bin/json/system/privilege/manifest/',
            {theme: 'wit', tokenLimit: 100, hintText: 'Start typing name'});
    });
    </script>'''

    # CREATE & UPDATE
    if request.method == "POST": 

        errors = []

        # check for errors
        if request.POST['user_class'] == "": 
            errors.append("Please select at least one user class")

        if request.POST['manifest'] == "": 
            errors.append("Please select at least one privilege manifest")

        # conclude
        if not errors: 
            # iterate through values and save individually
            for x in request.POST['user_class'].split(','): 
                c_user_class = UserClass.objects.get(pk=x)
                for y in request.POST['manifest'].split(','): 
                    c_manifest = PrivilegeManifest.objects.get(pk=y)
                    try: 
                        Privilege.objects.get(user_class__id=x, manifest__id=y)
                    except Privilege.DoesNotExist: 
                        Privilege.objects.create(user_class=c_user_class, manifest=c_manifest)

            response = 'Saved successfully'
            return HttpResponse(response_success(route=base_url + 'new/', response=response))

        else: 
            return HttpResponse(response_error(response=[errors]))

    #render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'obj': obj},
        context_instance=RequestContext(request)
    )


def ucp_flush(request, pk=None, process=False): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'user_class/'

    try: 
        instance = Privilege.objects.get(pk=pk)
    except KeyError: 
        return Auth.do_403()

    link = {'go': base_url + 'flush/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'Do you want to delete the grant <b>%s</b> from <b>%s</b> user class category?' % \
                           (instance.manifest, instance.user_class.name)
        return render_to_response(request.session["style"]+'/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page},
                                  context_instance=RequestContext(request)
                                  )

    elif process: 
        instance.delete()
        return HttpResponse(response_success(route=base_url+second_base, response='Privilege was flushed'))


def uc_user(request):

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'uc_user/'

    page = Page(request)
    page.title = 'Users\' Class'
    page.icon = 'fa fa-list-alt'
    page.form_name = 'usersClass'
    page.breadcrumbs = ['Privileges', 'Associated User Class']

    obj = UserClassTies.pp.filter(status__exact=1)

    #url processing
    instance = UserClassTies()
    form = forms.FormUserClassTies(instance=instance)
    page.form_action = base_url + second_base + 'new/'
    template = base_template + 'manage.html'

    #script for form
    page.script = '''
    <script>

    $(document).ready(function(){
        $('#id_user_class').tokenInput('/bin/json/system/privilege/user_class/',
            {theme: 'wit', tokenLimit: 100, hintText: 'Start typing name'});
        $('#id_user').tokenInput('/bin/json/system/user/',
            {theme: 'wit', tokenLimit: 100, hintText: 'Start typing name'});
    });
    </script>'''

    # CREATE & UPDATE
    if request.method == "POST": 

        errors = []

        # check for errors
        if request.POST['user_class'] == "": 
            errors.append("Please select at least one user class")

        if request.POST['user'] == "": 
            errors.append("Please select at least one users")

        # conclude
        if not errors: 

            # iterate through values and save individually
            for x in request.POST['user_class'].split(','):
                c_user_class = UserClass.objects.get(pk=x)
                for y in request.POST['user'].split(','): 
                    c_user = Users.pp.get(pk=y)

                    UserClassTies.pp.filter(user=c_user, user_class__module=c_user_class.module).delete()
                    UserClassTies.pp.create(user_class=c_user_class, user=c_user)

            response = 'Saved successfully'
            return HttpResponse(response_success(route=base_url + 'user_class/', response=response))

        else: 
            return HttpResponse(response_error(response=[errors]))

    #render to browser
    return render_to_response(
        template,
        {'s': s, 'form': form, 'page': page, 'obj': obj},
        context_instance=RequestContext(request)
    )


def uc_user_delete(request, pk=None, process=False): 

    s = Auth().is_auth(request)
    if not s: 
        return Auth.routeLogin

    second_base = 'user_class/'

    try: 
        instance = UserClassTies.pp.get(pk=pk)
    except KeyError: 
        return Auth.do_403()

    link = {'go': base_url + 'uc_user-delete/process/'+str(pk)+'/', 'cancel': base_url+second_base}
    page = Page(request)

    if not process: 
        page.description = 'Do you want to remove <b>%s [%s %s]</b> from the user class <b>%s</b>?' % \
                           (instance.user.username, instance.user.firstname, instance.user.lastname,
                            instance.user_class.name)
        return render_to_response(request.session["style"]+'/layout/snippets/delete-confirmation.html',
                                  {'link': link, 'page': page},
                                  context_instance=RequestContext(request)
                                  )

    elif process: 
        instance.delete()
        return HttpResponse(response_success(route=base_url+second_base, response='Removed Successfully'))


def index(request):

    page = Page(request)
    page.title = _('View Privileges')
    page.icon = 'fa fa-key'
    page.body_class = 'error-page sb-l-o sb-r-c'

    template = "system/privilege/privileges.html"

    return render_to_response(
        template,
        {'data': page},
        context_instance=RequestContext(request)
    )
