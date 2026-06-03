from django import forms
from django.contrib.auth.forms import AuthenticationForm


class ClinicLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
    )
