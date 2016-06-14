import os
from django.conf import settings

from django.db import models
from packages.bin.bin import format_alias
from packages.bin.extras.thumbs import ImageWithThumbsField
from packages.bin.middleware.syslicense import PostPrincipal, SysLicense as LIC
from packages.bin.resources import COUNTRIES, STATE_NG
from packages.hr.hr_personnel.models import Basic
from packages.system.bin import path_and_rename

USERTYPES = (
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    ('basic', 'Basic'),
    ('guest', 'Guest'),
)


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


class Contact(models.Model):
    name = models.CharField(max_length=125)
    is_coy = models.BooleanField(default=False)
    company_name = models.CharField(max_length=125, null=True, blank=True)
    phone = models.CharField(max_length=55, null=True, blank=True)
    email = models.CharField(max_length=125, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    line1 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=55, null=True, blank=True)
    state = models.CharField(max_length=55, null=True, blank=True, choices=STATE_NG)
    country = models.CharField(max_length=125, null=True, blank=True, choices=COUNTRIES, default='Nigeria')
    address = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)


class License(models.Model):
    company = models.ForeignKey(Contact, related_name='license', null=True, blank=True)
    company_name = models.CharField(max_length=125)
    company_logo_raw = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    company_logo = ImageWithThumbsField(
        upload_to=path_and_rename,
        sizes=((134, 29), (268, 58), (536, 116)),
        null=True,
        blank=True
    )
    company_address = models.TextField(null=True, blank=True)
    report_banner_portrait = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    report_banner_landscape = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    admin_email = models.EmailField()
    default_url = models.CharField(max_length=55, null=True, blank=True)
    default_module = models.ForeignKey(Module, related_name='license_default_module', null=True, blank=True)
    sys = models.CharField(max_length=25, unique=True)
    lid = models.CharField(max_length=55, blank=True, null=True, unique=True)
    modules = models.ManyToManyField(Module, related_name='license_modules')
    auth_email = models.EmailField(max_length=125, null=True, blank=True)
    auth_password = models.CharField(max_length=125, null=True, blank=True)
    smtp_host = models.CharField(max_length=125, null=True, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    use_tls = models.BooleanField(default=False)
    c_status = models.PositiveSmallIntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)

    objects = models.Manager()
    pp = PostPrincipal()

    def __unicode__(self):
        return self.company_name


class Subscription(models.Model):
    license = models.ForeignKey(License, related_name='license_subscription')
    expiry = models.DateField()
    status = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return str(self.expiry)


class Users(models.Model):
    profile = models.OneToOneField(Basic, related_name="users_profile", null=True, blank=True)
    username = models.CharField(max_length=55)
    password = models.CharField(max_length=125)
    usertype = models.CharField(max_length=55, default='basic', choices=USERTYPES)
    email = models.CharField(max_length=125)
    firstname = models.CharField(max_length=55, null=True, blank=True)
    lastname = models.CharField(max_length=55, null=True, blank=True)
    active = models.BooleanField(default=True)
    first_time = models.BooleanField(default=True)
    launched = models.BooleanField(default=False)
    logged_out = models.DateTimeField(auto_now=True,)
    
    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()
    
    def __unicode__(self):
        return "%s (%s %s)" % (self.email, self.firstname, self.lastname)
    
    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def alt_save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)

    def get_privileges(self):
        privileges = self.user_privilege.all()
        p = []
        for x in privileges:
            p.append(x.get_privileges())

        return p

    def get_expiry(self):
        try:
            license = License.objects.get(sys=self.sys, lid=self.lid)
            expiry = license.license_subscription.filter(status=1)[0]
            return expiry.expiry
        except IndexError:
            return None

    def reset_password(self):
        from hashlib import sha1
        from packages.bin.lib import random_chars

        raw_password = next(random_chars(8))

        self.password = sha1(raw_password).hexdigest()
        self.first_time = 1
        self.alt_save()

        return raw_password


class PrivilegeManifest(models.Model):
    module = models.ForeignKey(Module, related_name="module_privilege_manifest")
    name = models.CharField(max_length=25)
    alias = models.CharField(max_length=25)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def __unicode__(self):
        return "%s/%s" % (self.module.alias, self.name)

    def get_name(self):
        return "%s/%s" % (self.module.alias, self.name)

    def save(self, *args, **kwargs):
        self.alias = self.name.replace(" ", "_").lower()
        super(self.__class__, self).save(*args, **kwargs)


class UserClass(models.Model):
    module = models.ForeignKey(Module, related_name="module_user_class")
    name = models.CharField(max_length=55)
    alias = models.CharField(max_length=55)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def __unicode__(self):
        return "%s/%s" % (self.module.name, self.name)

    def save(self, *args, **kwargs):
        self.alias = self.name.replace(" ", "_").lower()
        super(self.__class__, self).save(*args, **kwargs)


class Privilege(models.Model):
    user_class = models.ForeignKey(UserClass, related_name="user_class_privilege")
    manifest = models.ForeignKey(PrivilegeManifest, related_name="manifest_privilege")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)


class PrivilegeUser(models.Model):
    user = models.ForeignKey(Users, related_name="user_privilege")
    manifest = models.ForeignKey(PrivilegeManifest, related_name="manifest_privilege_user")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)


class UserClassTies(models.Model):
    user = models.ForeignKey(Users, related_name="users_user_class")
    user_class = models.ForeignKey(UserClass, related_name="user_class_users")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s/%s" % (self.user_class.module.name, self.user_class.name)


class Report(models.Model):
    module = models.ForeignKey(Module, related_name="module_report")
    name = models.CharField(max_length=55)
    alias = models.CharField(max_length=55)
    file_url = models.CharField(max_length=225)
    type = models.CharField(max_length=12, null=True, blank=True)
    ext = models.CharField(max_length=5, null=True, blank=True)

    mac = models.ForeignKey(Users, related_name="users_report")
    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.PositiveSmallIntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.alias = format_alias(self.name)
        #self.lid = LIC.lid
        #self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # let us delete the physical file before deleting the data from the db
        f = os.path.join(settings.MEDIA_ROOT, self.file_url)
        os.path.exists(f) and os.remove(f)
        super(self.__class__, self).delete(*args, **kwargs)

    def alt_delete(self, *args, **kwargs):
        super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Scheduler(models.Model):
    c_status = models.PositiveSmallIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.IntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)


class Cron(models.Model):
    module = models.ForeignKey(Module, related_name="module_cron")
    name = models.CharField(max_length=55)
    frequency = models.CharField(max_length=25)
    note = models.TextField(null=True, blank=True)
    c_status = models.PositiveSmallIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.IntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
        pass


class CronLog(models.Model):
    cron = models.ForeignKey(Cron, related_name="cron_log")
    module = models.ForeignKey(Module, related_name="module_cron_log")

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.IntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s >> %s" % (self.cron.name, self.modified)


class Notification(models.Model):
    module = models.ForeignKey(Module, related_name="module_notification")
    handle = models.ForeignKey(Basic, null=True, blank=True, related_name="profile_notification")
    subscription_handle = models.CharField(max_length=125, null=True, blank=True)  # e.g. hr_admin
    name = models.CharField(max_length=125)
    alias = models.CharField(max_length=125, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=125, null=True, blank=True)
    number = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.IntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.number = self.notification_log.filter(c_status=1).count()
        self.alias = format_alias(self.name)
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class NotificationLog(models.Model):
    notification = models.ForeignKey(Notification, related_name="notification_log")
    subject = models.CharField(max_length=125, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    profile = models.ForeignKey(Basic, null=True, blank=True, related_name="profile_log_notification")
    profile_by = models.ForeignKey(Basic, null=True, blank=True, related_name="profile_r_notification")
    c_status = models.PositiveSmallIntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    status = models.IntegerField(default=1)
    sys = models.CharField(max_length=25, default="")
    lid = models.CharField(max_length=25, default="")

    objects = models.Manager()
    pp = PostPrincipal()

    def save(self, *args, **kwargs):
        self.lid = LIC.lid
        self.sys = LIC.sys
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
