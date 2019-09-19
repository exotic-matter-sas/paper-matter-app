from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import EmailField

from core.models import FTLUser


class FTLUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = ("email",)


class FTLAuthenticationForm(AuthenticationForm):
    username = EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    def clean_username(self):
        email_ = self.cleaned_data['username']
        return email_.lower()
