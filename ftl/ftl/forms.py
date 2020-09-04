#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import EmailField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_registration.forms import RegistrationForm

from core.models import (
    FTLUser,
    FTLOrg,
    permissions_names_to_objects,
    FTL_PERMISSIONS_USER,
    org_hash_validator,
)


class FTLUserCreationForm(RegistrationForm):
    """
    Form for user creation in an existing org
    """

    class Meta(RegistrationForm.Meta):
        model = FTLUser


class FTLCreateOrgAndFTLUser(RegistrationForm):
    """
    Form for org creation with first user
    """

    org_name = forms.CharField(
        label=_("Organization name*"),
        max_length=100,
        widget=forms.TextInput(attrs={"autofocus": ""}),
        help_text=_(
            "It's the name of your Paper Matter personal workspace, try to choose "
            "something unique (eg. based on your first and last name or company name)."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove default autofocus on email field
        del self.fields["email"].widget.attrs["autofocus"]
        # add the mandatory asterisk to existing label
        self.fields["email"].label = f"{self.fields['email'].label}*"
        self.fields["password1"].label = f"{self.fields['password1'].label}*"
        self.fields["password2"].label = f"{self.fields['password2'].label}*"

    class Meta(RegistrationForm.Meta):
        model = FTLUser
        fields = (
            "org_name",
            "email",
        )

    def clean_org_name(self):
        name_ = self.cleaned_data["org_name"]
        slug = slugify(name_)

        if FTLOrg.objects.filter(slug=slug).exists():
            raise forms.ValidationError(_("Organization already exists"))

        # Validators in model are not called automatically. They are only if used with ModelForm.
        # Here the model associated with ModelForm is FTLUser, so we have to manually validate the org slug.
        org_hash_validator(slug)

        return name_

    def save(self, commit=True):
        user = super().save(commit=False)

        org_name_cleaned = self.cleaned_data["org_name"]
        ftl_org = FTLOrg()
        ftl_org.name = org_name_cleaned
        ftl_org.slug = slugify(org_name_cleaned)
        ftl_org.save()

        user.org = ftl_org
        user.is_superuser = False
        user.is_staff = False
        user.save()

        user.user_permissions.set(permissions_names_to_objects(FTL_PERMISSIONS_USER))
        user.save()

        return super().save(commit)


class FTLAuthenticationForm(AuthenticationForm):
    username = EmailField(widget=forms.TextInput(attrs={"autofocus": True}))

    def clean_username(self):
        email_ = self.cleaned_data["username"]
        return email_.lower()
