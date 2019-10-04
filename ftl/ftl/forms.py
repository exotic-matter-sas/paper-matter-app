from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import EmailField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_registration.forms import RegistrationForm

from core.models import FTLUser, FTLOrg, permissions_names_to_objects, FTL_PERMISSIONS_USER


class FTLUserCreationForm(RegistrationForm):
    """
    Form for user creation in an existing org
    """

    class Meta(RegistrationForm.Meta):
        model = FTLUser


class FTLCreateOrgAndUser(RegistrationForm):
    """
    Form for org creation with first user
    """
    org_name = forms.CharField(label=_('Organization name'), max_length=100)

    class Meta(RegistrationForm.Meta):
        model = FTLUser

    def clean_org_name(self):
        name_ = self.cleaned_data['org_name']
        slug = slugify(name_)
        org_exists = FTLOrg.objects.filter(slug=slug)
        if org_exists:
            raise forms.ValidationError(_("Org already exists"))
        return name_

    def save(self, commit=True):
        user = super().save(commit=False)

        org_name_cleaned = self.cleaned_data['org_name']
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
    username = EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    def clean_username(self):
        email_ = self.cleaned_data['username']
        return email_.lower()
