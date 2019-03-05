from django.contrib.auth.forms import UserCreationForm, UsernameField, forms
from django.contrib.auth.models import User
from django.forms.models import fields_for_model

from .models import FTLUser, FTLOrg


class FTLUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username",)
        field_classes = {'username': UsernameField}

    def save(self, commit=True):
        """Create FTLUser after django user creation"""
        user = super().save()
        org = FTLOrg.objects.get(slug='exotic-matter')
        ftl_user = FTLUser(ftl_user=user,
                           org=org)
        ftl_user.save()

        return user


class SelectOrganizationToLoginForm(forms.Form):

    organization_slug = fields_for_model(FTLOrg)['slug']
