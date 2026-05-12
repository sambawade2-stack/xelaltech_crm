from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CompanySettings


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'bio', 'avatar', 'theme', 'language']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'},
                                     choices=[('fr', 'Français'), ('en', 'English')]),
        }


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ['name', 'tagline', 'logo', 'email', 'phone', 'address', 'website', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'tagline': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'currency': forms.TextInput(attrs={'class': 'form-input'}),
        }


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class UserCreateForm(UserCreationForm):
    """Admin-only form to create a user with a role."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'role', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-input'}),
            'email':      forms.EmailInput(attrs={'class': 'form-input'}),
            'username':   forms.TextInput(attrs={'class': 'form-input'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['password1', 'password2']:
            self.fields[f].widget.attrs['class'] = 'form-input'


class UserEditForm(forms.ModelForm):
    """Admin-only form to edit role and status."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-input'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
        }
