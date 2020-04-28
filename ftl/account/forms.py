#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import FTLUser, email_hash_validator


class EmailSendForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)

    def clean_email(self):
        c_email = self.cleaned_data["email"]

        if FTLUser.objects.filter(email=c_email).exists():
            raise forms.ValidationError(_("Email is already used by someone else."))

        email_hash_validator(c_email)


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autofocus": True}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        ck_password = self.cleaned_data["password"]
        if not self.user.check_password(ck_password):
            raise forms.ValidationError(_("Incorrect password"))
        return ck_password
