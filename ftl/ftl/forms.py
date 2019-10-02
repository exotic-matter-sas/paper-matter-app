from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import EmailField
from django_registration.forms import RegistrationForm

from core.models import FTLUser


class FTLUserCreationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = FTLUser


class FTLAuthenticationForm(AuthenticationForm):
    username = EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    def clean_username(self):
        email_ = self.cleaned_data['username']
        return email_.lower()
