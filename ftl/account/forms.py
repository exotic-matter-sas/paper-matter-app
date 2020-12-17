#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import pytz
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _, check_for_language

from core.models import FTLUser, email_hash_validator


class EmailSendForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)

    def clean_email(self):
        c_email = self.cleaned_data["email"]

        if FTLUser.objects.filter(email=c_email).exists():
            raise forms.ValidationError(_("Email is already used by someone else."))

        email_hash_validator(c_email)

        return c_email


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


class SettingsAccountForm(forms.Form):
    TZ_LIST = [(None, "--")] + [(t, t) for t in pytz.common_timezones]
    LANG_LIST = [(None, "--")] + [(k, v) for k, v in getattr(settings, "LANGUAGES", [])]
    tz = forms.ChoiceField(label=_("Timezone"), choices=TZ_LIST,)
    lang = forms.ChoiceField(label=_("Language"), choices=LANG_LIST,)

    def clean_lang(self):
        lang = self.cleaned_data["lang"]
        if not check_for_language(lang):
            raise ValidationError("Unsupported language")
        return lang

    def clean_tz(self):
        tz = self.cleaned_data["tz"]
        if tz not in pytz.common_timezones:
            raise ValidationError("Unsupported timezone")
        return tz
