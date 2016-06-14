from django import forms
from django.forms import ModelForm

from packages.system.models import Users

class FormLogin(ModelForm):
    class Meta:
        model = Users
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder':'Username', 'class':'form-control'}),
            'password': forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-control'}),
        }
        labels = {
            'username' : "Username",
            'password' : "Password",
        }


class FormRegisterNew(ModelForm):
    
    class Meta:
        model = Users
        fields = ['profile', 'username', 'password', 'usertype', 'email', 'firstname', 'lastname']
        widgets = {
            'profile': forms.TextInput(attrs={'class':'form-control'}),
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'password': forms.PasswordInput(attrs={'class':'form-control'}),
            'usertype': forms.Select(attrs={'class':'form-control pp-chosen'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
            'firstname': forms.TextInput(attrs={'class':'form-control'}),
            'lastname': forms.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'profile' : "Append to Profile (If Necessary)",
            'username' : "Username",
            'password' : "Password",
            'usertype' : "User Type",
            'email' : "Email",
            'firstname' : "First Name",
            'lastname' : "Last Name",
        }

class FormRegister(ModelForm):
    
    class Meta:
        model = Users
        fields = ['profile', 'username', 'usertype', 'email', 'firstname', 'lastname']
        widgets = {
            'profile': forms.TextInput(attrs={'class':'form-control'}),
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'password': forms.TextInput(attrs={'class':'form-control'}),
            'usertype': forms.Select(attrs={'class':'form-control pp-chosen'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
            'firstname': forms.TextInput(attrs={'class':'form-control'}),
            'lastname': forms.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'profile' : "Append to Profile",
            'username' : "Username",
            'password' : "Password",
            'usertype' : "User Type",
            'email' : "Email",
            'firstname' : "First Name",
            'lastname' : "Last Name",
        }