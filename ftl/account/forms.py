#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django import forms
from django.utils.translation import ugettext_lazy as _


class EmailSendForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)


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
            raise forms.ValidationError("Incorrect password")
        return ck_password
