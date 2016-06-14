from django.db import models
from packages.hr.hr_personnel.models import Basic

USERTYPES = (
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    ('basic', 'Basic'),
    ('guest', 'Guest'),
)


#===============================================================================
# MODULES
#===============================================================================
class Module(models.Model):
    name = models.CharField(max_length=25)
    alias = models.CharField(max_length=25)
    author = models.CharField(max_length=55, blank=True, null=True)
    version = models.CharField(max_length=12, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.alias = self.name.replace(" ", "_").lower()
        super(Module, self).save(*args, **kwargs)


#===============================================================================
# USERS
#===============================================================================
class Users(models.Model):
    profile = models.OneToOneField(Basic, null=True, blank=True)
    username = models.CharField(max_length=55, unique=True)
    password = models.CharField(max_length=125)
    usertype = models.CharField(max_length=55, default='basic', choices=USERTYPES)
    email = models.CharField(max_length=125, null=True, blank=True)
    firstname = models.CharField(max_length=55, null=True, blank=True)
    lastname = models.CharField(max_length=55, null=True, blank=True)
    active = models.BooleanField(default=0)
    first_time = models.BooleanField(default=1)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)

    def get_privileges(self):
        privileges = self.user_privilege.all()
        p = []
        for x in privileges:
            p.append(x.get_privileges())

        return p


#===============================================================================
# PRIVILEGES
#===============================================================================
class PrivilegeManifest(models.Model):
    module = models.ForeignKey(Module, related_name="module_privilege_manifest")
    name = models.CharField(max_length=25)
    alias = models.CharField(max_length=25)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')

    def __unicode__(self):
        return "%s/%s" % (self.module.alias, self.name)

    def get_name(self):
        return "%s/%s" % (self.module.alias, self.name)


class UserClass(models.Model):
    module = models.ForeignKey(Module, related_name="module_user_class")
    name = models.CharField(max_length=55)
    alias = models.CharField(max_length=55)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')

    def __unicode__(self):
        return "%s/%s" % (self.module.name, self.name)


class Privilege(models.Model):
    user_class = models.ForeignKey(UserClass, related_name="user_class_privilege")
    manifest = models.ForeignKey(PrivilegeManifest, related_name="manifest_privilege")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')


class PrivilegeUser(models.Model):
    user = models.ForeignKey(Users, related_name="user_privilege")
    manifest = models.ForeignKey(PrivilegeManifest, related_name="manifest_privilege_user")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')


class UserClassTies(models.Model):
    user = models.ForeignKey(Users, related_name="users_user_class")
    user_class = models.ForeignKey(UserClass, related_name="user_class_users")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')


class Notification(models.Model):
    code = models.TextField()
    number = models.IntegerField(default=1)
    pattern = models.TextField()
    url = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default='dmc')
    lid = models.CharField(max_length=25, default='shareware')

    def __unicode__(self):
        return self.msg