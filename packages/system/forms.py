from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _, ugettext

from packages.system.models import *


class FormLogin(ModelForm):
    class Meta:
        model = Users
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
        }
        labels = {
            'username': "Username",
            'password': "Password",
        }


class FormChangePassword(forms.Form):
    old_password = forms.CharField(
        label=ugettext('Old password'),
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('Old password')}
        )
    )

    new_password = forms.CharField(
        label=ugettext('New password'),
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('New password')}
        )
    )

    confirm_password = forms.CharField(
        label=ugettext('Confirm password'),
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('Confirm password')}
        )
    )


class FormForgotPassword(forms.Form):
    email = forms.CharField(
        label=ugettext('Email'),
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': _('Email')}
        )
    )


class FormRegisterNew(ModelForm):
    
    class Meta:
        model = Users
        fields = ['profile', 'usertype', 'email', 'firstname', 'lastname']
        widgets = {
            'profile': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'usertype': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'profile': "Append to Profile (If Necessary)",
            'username': "Username",
            'password': "Password",
            'usertype': "User Type",
            'email': "Email",
            'firstname': "First Name",
            'lastname': "Last Name",
        }


class FormRegister(ModelForm):
    
    class Meta:
        model = Users
        fields = ['profile', 'usertype', 'email', 'firstname', 'lastname']
        widgets = {
            'profile': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'usertype': forms.Select(attrs={'class': 'form-control pp-chosen'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'profile': "Append to Profile",
            'username': "Username",
            'password': "Password",
            'usertype': "User Type",
            'email': "Email",
            'firstname': "First Name",
            'lastname': "Last Name",
        }


class FormModule(ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'author', 'version', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Module Name', 'class': 'form-control'}),
            'author': forms.TextInput(attrs={'placeholder': 'Author', 'class': 'form-control'}),
            'version': forms.TextInput(attrs={'placeholder': 'Version', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'class': 'form-control'}),
        }
        labels = {
            'name': "Module Name",
            'author': "Author/Developer",
            'version': "Version",
            'description': "Description",
        }


class FormPrivilegeManifest(ModelForm):
    class Meta:
        model = PrivilegeManifest
        fields = ['module', 'name']
        widgets = {
            'module': forms.Select(attrs={'placeholder': 'Select a Module', 'class': 'form-control pp-chosen'}),
            'name': forms.TextInput(attrs={'placeholder': 'Manifest Name', 'class': 'form-control'}),
        }
        labels = {
            'module': "Select Module",
            'name': "Name",
        }
        help_texts = {
            'name': "Manifest should look in the form \"<sub_module>:<privilege>\" e.g. user:create, category:manage, "
                    "payment:approve, hr_leave:approve_as_supervisor"
        }


class FormUserClass(ModelForm):
    class Meta:
        model = UserClass
        fields = ['module', 'name']
        widgets = {
            'module': forms.Select(attrs={'placeholder': 'Select a Module', 'class': 'form-control pp-chosen'}),
            'name': forms.TextInput(attrs={'placeholder': 'User Class e.g. UC1', 'class': 'form-control'}),
        }
        labels = {
            'module': "Select Module",
            'name': "User Class",
        }


class FormPrivilege(ModelForm):
    class Meta:
        model = Privilege
        fields = ['user_class', 'manifest']
        widgets = {
            'user_class': forms.TextInput(attrs={'placeholder': 'Select User Class', 'class': 'form-control'}),
            'manifest': forms.TextInput(attrs={'placeholder': 'Select from privilege manifests',
                                               'class': 'form-control'}),
        }
        labels = {
            'user_class': "User Class",
            'manifest': "Manifest",
        }


class FormPrivilegeUser(ModelForm):
    class Meta:
        model = PrivilegeUser
        fields = ['user', 'manifest']
        widgets = {
            'user': forms.TextInput(attrs={'placeholder': 'Select User', 'class': 'form-control'}),
            'manifest': forms.TextInput(attrs={'placeholder': 'Select from privilege manifests',
                                               'class': 'form-control'}),
        }
        labels = {
            'user': "Username",
            'manifest': "Manifest",
        }


class FormUserClassTies(ModelForm):
    class Meta:
        model = UserClassTies
        fields = ['user_class', 'user']
        widgets = {
            'user': forms.TextInput(attrs={'placeholder': 'Select User', 'class': 'form-control'}),
            'user_class': forms.TextInput(attrs={'placeholder': 'Select User Classes',
                                                 'class': 'form-control pp-chosen'}),
        }
        labels = {
            'user': "Username",
            'user_class': "User Classes",
        }


class FormLicense(ModelForm):

    class Meta:
        model = License
        fields = ['company', 'company_name', 'company_logo_raw', 'company_logo', 'company_address',
                  'report_banner_portrait', 'report_banner_landscape',
                  'admin_email', 'default_module', 'default_url', 'sys', 'lid', 'modules',
                  'auth_email', 'auth_password', 'smtp_host', 'smtp_port', 'use_tls']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_logo_raw': forms.FileInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control'}),
            'report_banner_portrait': forms.FileInput(attrs={'class': 'form-control'}),
            'report_banner_landscape': forms.FileInput(attrs={'class': 'form-control'}),
            'admin_email': forms.TextInput(attrs={'class': 'form-control'}),
            'default_module': forms.Select(attrs={'class': 'form-control'}),
            'default_url': forms.TextInput(attrs={'class': 'form-control'}),
            'sys': forms.TextInput(attrs={'class': 'form-control'}),
            'lid': forms.TextInput(attrs={'class': 'form-control'}),
            'modules': forms.TextInput(attrs={'class': 'form-control'}),
            'auth_email': forms.TextInput(attrs={'class': 'form-control'}),
            'auth_password': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_host': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'company': _("Select CRM Object"),
            'company_name': _("Company Name"),
            'company_logo_raw': _("Company Logo [No format]"),
            'company_logo': _("Company Logo [536 x 116]"),
            'company_address': _("Company Address"),
            'report_banner_portrait': _("Upload Report Banner [Portrait]"),
            'report_banner_landscape': _("Upload Report Banner [Landscape]"),
            'admin_email': _("Administrator Email"),
            'sys': _("Company Secret Key [Sys]"),
            'lid': _("License ID"),
            'modules': _("Select Some Modules"),
            'auth_email': _("SMTP Email Address"),
            'auth_password': _("SMTP Password"),
            'smtp_host': _("SMTP Host"),
            'smtp_port': _("SMTP Port"),
            'use_tls': _("Use TLS"),
        }


class FormSubscription(ModelForm):

    class Meta:
        model = Subscription
        fields = ['expiry']
        widgets = {
            'license': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry': forms.TextInput(attrs={'class': 'form-control datepicker'}),
        }
        labels = {
            'expiry': "Enter License Expiry Date",
        }