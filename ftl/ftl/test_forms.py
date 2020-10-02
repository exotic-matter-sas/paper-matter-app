#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from unittest.mock import patch

from django.test import TestCase
from django_otp.plugins.otp_static.models import StaticToken

from ftests.tools.setup_helpers import setup_org, setup_user, setup_2fa_static_device, setup_2fa_totp_device, \
    setup_2fa_fido2_device
from ftl.otp_plugins.otp_ftl.forms import StaticDeviceCheckForm, TOTPDeviceCheckForm, \
    StaticDeviceForm, TOTPDeviceForm
from .forms import FTLUserCreationForm
from ftests.tools import test_values as tv


class FtlUserCreationFormTests(TestCase):
    def setUp(self):
        self.org = setup_org()

    def test_form_render_email_input(self):
        """Form render email input"""
        form = FTLUserCreationForm()
        self.assertIn("Email address", form.as_p())

    def test_form_refuse_blank_email(self):
        """Form refuse blank email"""
        form = FTLUserCreationForm(
            data={"email": "", "password1": tv.USER1_PASS, "password2": tv.USER1_PASS,}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_refuse_non_unique_email(self):
        """Form refuse non unique email"""
        setup_user(self.org, email=tv.USER1_EMAIL)

        form = FTLUserCreationForm(
            data={
                "email": tv.USER1_EMAIL,
                "password1": tv.USER2_PASS,
                "password2": tv.USER2_PASS,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
