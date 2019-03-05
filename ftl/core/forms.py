from django.contrib.auth.forms import UserCreationForm, UsernameField, forms
from django.contrib.auth.models import User
from django.forms.models import fields_for_model
from django.shortcuts import get_object_or_404

from .models import FTLUser, FTLOrg


class FTLUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username",)
        field_classes = {'username': UsernameField}

    def save(self, org_slug, commit=True):
        """Create FTLUser after django user creation"""
        user = super().save()
        org = get_object_or_404(FTLOrg, slug=org_slug)
        ftl_user = FTLUser(user=user,
                           org=org)
        ftl_user.save()

        return user


class SelectOrganizationToLoginForm(forms.Form):

    organization_slug = fields_for_model(FTLOrg)['slug']
