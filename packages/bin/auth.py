from django.shortcuts import HttpResponseRedirect
from packages.bin.notifier import Notify
from packages.system.models import Users
from packages.hr.hr_personnel.models import Basic


class Auth(object):

    request = None
    routeLogin = HttpResponseRedirect('/system/login/')
    
    def __init__(self):
        return None


    @staticmethod
    def isAuth(s):

        s.session['notification_count'], s.session['notifications'] = Notify.render()

        #check authentication status and return boolean
        try:
            if s.session['auth']:
                return True
            else:
                pass
        except KeyError:
            #trap the link browser attempted for redirection from login
            s.session['redir'] = '/'


    def deAuth(self, s):
        try:
            del s.session['auth']
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
    def getPrivileges(user):
        # fetch list of associated user classes
        x = []
        user_classes = user.users_user_class.all()
        for m in user_classes:
            for p in m.user_class.user_class_privilege.all():
                x.append(p.manifest.get_name())

        return x


    @staticmethod
    def p_auth(request, privilege=None, privileges=[]):
        # check if user is privileged
        if request.session['auth_username'] == 'admin':
            return True

        try:
            user = Users.pp.get(id=request.session['auth_id'])

        except Users.DoesNotExist:
            return False

        if privilege is not None:
            try:
                Auth.getPrivileges(user).index(privilege)
                return True

            except ValueError:
                return False

        else:
            for privilege in privileges:
                try:
                    Auth.getPrivileges(user).index(privilege)
                    check = True

                except ValueError:
                    check = False

                if check is True:
                    return True

            return False