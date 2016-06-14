from datetime import datetime
import traceback
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, render_to_response
from django.template import RequestContext
from django.utils.translation import gettext as _
from packages.bin.cronjob import CronJob
from packages.system.models import Users
from packages.hr.hr_personnel.models import Basic


class Auth(object):

    request = None
    routeLogin = HttpResponseRedirect('/system/login/')
    
    def __init__(self, do_cron=True):
        # always run system cron - False method prevents cron from running twice in microseconds to prevent
        # duplicating some functions
        #if do_cron:
            #CronJob()
        pass

    @staticmethod
    def is_auth(s):
        #check authentication status and return boolean
        try:
            if s.session['auth']:
                return True
            else:
                pass
        except KeyError:
            #trap the link browser attempted for redirection from login
            s.session['redir'] = '/'

    def do_logout(self, s, log_timeout=True):

        from packages.system.models import Module

        if log_timeout:
            try:
                users = Auth.whoami(s, 'users')
                users.logged_out = datetime.now()
                users.save()
            except Exception:
                pass

        try:
            del s.session['auth']

        except (KeyError, ValueError):
            pass

        for module in Module.objects.all():
            s.session["app_" + module.alias] = False
            s.session["app_d_" + module.alias] = False
        
        return self.routeLogin

    def do_logout_final(self, s):

        try:
            users = Auth.whoami(s, 'users')
            users.logged_out = datetime.now()
            users.save()
        except Exception:
            pass

        try:
            del s.session['auth']

        except (KeyError, ValueError):
            pass

        try:
            del s.session['auth_id']
            del s.session['auth_username']
            del s.session['auth_fullname']

        except (KeyError, ValueError):
            pass

        try:
            del s.session['auth_idp']
            del s.session['auth_email']
            del s.session['auth_thumb_64']

        except (KeyError, ValueError):
            pass

        try:
            del s.session['sys']
            del s.session['lid']

        except (KeyError, ValueError):
            pass

        return self.routeLogin

    @staticmethod
    def whoami(request, method=None):
        if method is None:
            return Basic.objects.get(pk=request.session['auth_idp'])

        else:
            return Users.objects.get(pk=request.session['auth_id'])

    @staticmethod
    def usertype(request):
        return Users.pp.get(pk=request.session['auth_id']).usertype

    @staticmethod
    def get_privileges(user):
        # fetch list of associated user classes
        x = []
        user_classes = user.users_user_class.all()
        for m in user_classes:
            for p in m.user_class.user_class_privilege.all():
                x.append(p.manifest.get_name())

        return x

    @staticmethod
    def p_auth(request, privilege=None, privileges=None):
        for k, v in request.session.iteritems():
            #print k, v
            pass

        # check if user is privileged
        if request.session['auth_username'] == 'admin':
            return True

        try:
            user = Users.pp.get(id=request.session['auth_id'])
        except Users.DoesNotExist:
            return False

        if privileges is not None:
            for privilege in privileges:
                try:
                    Auth.get_privileges(user).index(privilege)
                    return True
                except ValueError:
                    pass

            return False

        else:
            try:
                Auth.get_privileges(user).index(privilege)
                return True

            except ValueError:
                return False

    @staticmethod
    def do_404(request=None):
        """
        Page not found
        """
        from django.conf import settings
        from packages.bin.bin import Page

        page = Page(request)
        page.script = '''
        <script>
        window.location.href = '%s/system/error/404/';
        </script>
        ''' % settings.BASE_URL

        return render_to_response(
            'system/script.html',
            {'page': page, },
            context_instance=RequestContext(request)
        )

    @staticmethod
    def do_403(request=None, re_route=None):
        """
        Forbidden
        """
        from django.conf import settings
        from packages.bin.bin import Page

        page = Page(request)
        page.script = '''
        <script>
        //window.location.href = '%s/system/error/403/';
        window.location.href = '%s/system/login/';
        </script>
        ''' % settings.BASE_URL

        request.session['error-route'] = re_route

        return render_to_response(
            'system/script.html',
            {'page': page,},
            context_instance=RequestContext(request)
        )

    @staticmethod
    def ldap(username, password, link=None, retrieve_all=False):
        import ldap

        try:
            #ld = ldap.initialize("ldap://ptad.gov.ng:389")
            ld = ldap.initialize("ldap://icrc.gov.ng:389")
            ld.set_option(ldap.OPT_REFERRALS, 0)
            ld.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            ld.simple_bind_s(username, password)
            if ld.whoami_s() is not None:
                if retrieve_all:
                    # QUERY ALL DATA
                    basedn = "dc=icrc,dc=gov,dc=ng"
                    results = ld.search_s(basedn, ldap.SCOPE_SUBTREE)
                    people = list()
                    for dn, entry in results:
                        people.append(entry)

                    return people

                username = "%s@icrc.gov.ng" % username
                return Users.pp.get(email=username)
            else:
                return False

        except Exception:
            print traceback.print_exc()
            return False
