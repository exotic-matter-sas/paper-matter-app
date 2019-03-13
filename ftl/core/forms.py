from django.contrib.auth.forms import UserCreationForm, UsernameField, forms
from django.contrib.auth.models import User
from django.forms.models import fields_for_model

from .models import FTLOrg


class FTLUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username",)
        field_classes = {'username': UsernameField}


class SelectOrganizationToLoginForm(forms.Form):

    organization_slug = fields_for_model(FTLOrg)['slug']
