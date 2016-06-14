from hashlib import sha1

from packages.bin.auth import Auth
from packages.bin.bin import Page, Actions, Table
from packages.bin.lib import get_thumb

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from packages.system.forms import FormLogin, FormRegister, FormRegisterNew
from packages.system.models import Users
from packages.hr.hr_personnel.models import Basic

# Create your views here.

#===============================================================================
# LOGIN
#===============================================================================
def login(request, q=None):
    if request.method == "POST":
        form = FormLogin(request.POST)
        form.action = '/system/login/process/'
        
        usernameStr = request.POST['username']
        passwordStr = request.POST['password']
        print passwordStr
        
        # check for the authenticity of username and password passed
        try:
            user = Users.objects.get(username=usernameStr, password=sha1(passwordStr).hexdigest())
            
            if user is not None and user.active == 0:
                error_msg = "You account isn't active yet or is suspended. Please contact your system administrator"
                return render_to_response('login.html', {'form':form, 'formError':error_msg}, context_instance=RequestContext(request))
                
            elif user is not None and user.active == 1:
                request.session['auth'] = True
                request.session['auth_id'] = user.id
                request.session['auth_username'] = user.username
                request.session['auth_fullname'] = ""
                request.session['auth_email'] = ""

                try:
                    request.session['auth_idp'] = user.profile.id

                except (ValueError, AttributeError):
                    request.session['auth_idp'] = ""

                try:
                    request.session['auth_thumb_64'] = get_thumb(user.profile.picture.url, '64x64')

                except (ValueError, AttributeError):
                    request.session['auth_thumb_64'] = "/static/img/avatars/1.jpg"
                
                #let take the user to the link he/she expected expressly
                try:
                    #link = request.session['redir']
                    link = '/dashboard/'

                except KeyError:
                    link = '/dashboard/'
                 
                return HttpResponseRedirect(link)
            
            else:
                pass
            
        except (KeyError, AttributeError, Users.DoesNotExist):
            pass
        
        return render_to_response('login.html', {'form':form, 'formError':"Username and Password Mismatch"}, context_instance=RequestContext(request))
    
    else:
        form = FormLogin()
        form.action = '/system/login/process/'
        return render_to_response('login.html', {'form':form}, context_instance=RequestContext(request))

#===============================================================================
# LOGOUT
#===============================================================================
def logout(request):
    return Auth().deAuth(request)

#===============================================================================
# USER MANAGEMENT
#===============================================================================
base_url_admin = '/system/users/'
base_template_admin = 'system/users/snippets/'
def User(request):
    
    s = Auth().isAuth(request)
    if s == False:
        return Auth.routeLogin
    
    second_base_url = ''
    
    page = Page(request)
    page.title = 'User Management'
    page.icon = 'fa fa-group'
    page.breadcrumbs = ['User Management', 'View']
    page.errors = []
    
    obj = Users.objects.all()
    obj_settings = [
        {'link':base_url_admin+second_base_url+'update/', 'icon':Actions().Icon.edit},
        {'link':base_url_admin+second_base_url+'delete/', 'icon':Actions().Icon.delete},
    ]
    
    table = Table()
    table.cols = ['Username', 'User Type', 'Profile Name', 'Active', 'Reset Password']
    table.rows = []
    for val in obj:
        reset_link = "<a href='/system/users/reset-password/%s/' class='btn btn-xs btn-warning'>Reset Password</a>" % val.id
        
        if val.active == 0:
            btn_class = 'btn-success'
            btn_name = 'Activate'
            btn_link = '/system/users/status/activate/%s/' % val.id
        else:
            btn_class = 'btn-danger'
            btn_name = 'Deactivate'
            btn_link = '/system/users/status/deactivate/%s/' % val.id
            
        activate_link = "<a href='%s' class='btn btn-xs %s'>%s</a>" % (btn_link, btn_class, btn_name)
        
        table.rows.append({
            'id':val.id,
            'fields': [
                {'field':val.username},
                {'field':val.usertype},
                {'field':val.profile.get_fullname()},
                {'field':activate_link},
                {'field':reset_link}
            ]
        })
    
    return Auth.routeLogin if s == False else \
        render_to_response(base_template_admin+'list.html', {'s':s, 'table':table, 'settings':obj_settings, 'page':page})


def UserManage(request, pk=None):
    
    s = Auth().isAuth(request)
    if s == False:
        return Auth.routeLogin
    
    second_base_url = ''
    
    obj = Users() if pk == None else Users.objects.get(pk=pk)
    
    page = Page(request)
    page.title = 'User Management'
    page.icon = 'fa fa-group'
    page.form_name = 'user_management'
    page.form_action = base_url_admin+second_base_url+'new/'
    page.breadcrumbs = ['System', 'User Management']
    page.errors = []
    
    #script
    try:
        profile = ", prePopulate: [{'id':%d, name:'%s'}]" % (obj.profile.id, obj.profile.get_fullname())
        
    except (KeyError, AttributeError) as e:
        profile = ""
        pass
    
    page.script = '''<script>
        $(document).ready(function(){
            $('#id_profile').tokenInput('/bin/json/profile/', {theme:'wit', tokenLimit:1, hintText:'Start typing name' %s});
        });
        </script>''' % (profile)
        
    #create record
    if request.method != "POST" and pk == None:
        page.breadcrumbs.append('New')
        form = FormRegisterNew(instance=obj)
        
        return Auth.routeLogin if s == False else \
            render_to_response(base_template_admin+'manage.html', {'s':s, 'form':form, 'page':page}, context_instance=RequestContext(request))

    elif request.method != "POST" and pk is not None:
        page.form_action = base_url_admin+second_base_url+'update/'+str(pk)+'/'
        page.title = 'Update User: %s' % obj.username
        page.breadcrumbs.append('Update')
        page.request = request
        page.id = pk
        
        from django.forms.models import model_to_dict
        obj.email = obj.profile.email
        obj.firstname = obj.profile.firstname
        obj.lastname = obj.profile.lastname
        form = FormRegister(instance=obj, data=model_to_dict(obj))
        
        return render_to_response(base_template_admin+'manage.html', {'s':s, 'form':form, 'page':page}, context_instance=RequestContext(request))
    
    #process record
    elif request.method == "POST":
        page.breadcrumbs.append('Update')
        page.form_action = base_url_admin+second_base_url + 'new/' if pk == None else base_url_admin+second_base_url + 'update/'+str(pk)+'/'
        
        #do some non field specific validations
        if pk is None:
            form = FormRegisterNew(instance=obj, data=request.POST)
            if request.POST['password'] == "":
                page.non_field_errors = ['Please enter a valid password']
        else:
            form = FormRegister(instance=obj, data=request.POST)
        
        #validate and process
        if form.is_valid() and not page.non_field_errors:
            #do method to process
            posts = request.POST
            for post in posts:
                if hasattr(obj, post):
                    setattr(obj, post, form.cleaned_data[post])
            
            if pk == None:
                basic = Basic(reference=obj.username, firstname=obj.firstname, lastname=obj.lastname, email=obj.email, c_status=-1)
            else:
                basic = Basic.objects.get(pk=obj.profile.id)
                basic.reference = basic.reference or obj.username
                basic.firstname = obj.firstname
                basic.lastname = obj.lastname
                basic.email = obj.email
            
            basic.save()
            obj.profile = basic
            obj.save()
            return HttpResponseRedirect(base_url_admin+second_base_url)
        else:
            for f in form:
                page.errors.append(str(f.errors))
            
            return render_to_response(base_template_admin+'manage.html', {'s':s, 'form':form, 'page':page}, context_instance=RequestContext(request))
    
    else:
        pass

#---------->>> ADMIN USER DELETE
def UserDelete(request, pk=None, process=False):
    
    s = Auth().isAuth(request)
    if s == False:
        return Auth.routeLogin
    
    second_base_url = ''
    
    try:
        obj = Users.objects.get(pk=pk)
    except KeyError:
        HttpResponseRedirect('/404/hack/')
    
    link = {'go':base_url_admin+second_base_url+'delete/process/'+str(pk)+'/', 'cancel':base_url_admin+second_base_url}
    page = Page(request)
    
    if not process:
        page.description = 'You are about to delete a user: <b>%s</b>. How do you want to proceed?' % obj.username
        return render_to_response('layout/snippets/delete-confirmation.html', {'link':link, 'page':page}, context_instance=RequestContext(request))
    
    elif process:
        
        #check if profile user is auto generated by check for the c_status if -1, then delete
        try:
            profile = Basic.objects.get(pk=obj.profile.id, c_status=-1)
            profile.delete()
        except (KeyError, AttributeError):
            pass
        
        #delete user details
        obj.delete()
        return HttpResponseRedirect(base_url_admin+second_base_url)


def UserResetPassword(request, pk=None, process=False):
    
    s = Auth().isAuth(request)
    if s is False:
        return Auth.routeLogin
    
    second_base_url = ''
    
    try:
        obj = Users.objects.get(pk=pk)
    except KeyError:
        HttpResponseRedirect('/404/hack/')
    
    link = {
        'go': base_url_admin+second_base_url+'reset-password/process/'+str(pk)+'/',
        'cancel': base_url_admin+second_base_url
    }
    page = Page(request)
    page.confirmation_value = "Reset Password"
    
    if not process:
        page.description = 'You are about to reset <b>%s</b>\'s password. How do you want to proceed?' % obj.username
        return render_to_response('layout/snippets/delete-confirmation.html', {'link':link, 'page':page}, context_instance=RequestContext(request))
    
    elif process:
        obj.password = sha1("password").hexdigest()
        obj.save()
        return HttpResponseRedirect(base_url_admin+second_base_url)


def UserStatus(request, pk=None, method=None):
    
    s = Auth().isAuth(request)
    if s == False:
        return Auth.routeLogin
    
    second_base_url = ''
    
    try:
        obj = Users.objects.get(pk=pk)
    except KeyError:
        HttpResponseRedirect('/404/hack/')
    
    if method != None and pk != None:
        if method == 'activate':
            obj.active = 1
        elif method == 'deactivate':
            obj.active = 0
        else:
            HttpResponseRedirect('/404/hack/') 
            
        obj.save()
        return HttpResponseRedirect(base_url_admin+second_base_url)
    