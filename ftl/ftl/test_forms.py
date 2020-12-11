#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from unittest.mock import patch

from django.test import TestCase, override_settings
from django_otp.plugins.otp_static.models import StaticToken

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_user,
    setup_2fa_static_device,
    setup_2fa_fido2_device,
    setup_2fa_totp_device,
)
from ftl.otp_plugins.otp_ftl.forms import (
    StaticDeviceCheckForm,
    TOTPDeviceCheckForm,
    StaticDeviceForm,
    TOTPDeviceForm,
)
from .forms import FTLUserCreationForm, FTLCreateOrgAndFTLUser


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


@override_settings(FTL_ENABLE_SIGNUP_CAPTCHA=True)
class FTLCreateOrgAndFTLUserTests(TestCase):
    def test_captcha_render(self):
        form = FTLCreateOrgAndFTLUser(lang="fr")
        self.assertIn(
            '<label class="required" for="id_captcha_1">Are you human?*:</label>',
            form.as_p(),
        )


########################
# Otp_ftl plugin forms #
########################


class StaticDeviceCheckFormTests(TestCase):
    def setUp(self):
        self.org_1 = setup_org()
        self.org_2 = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        self.user_1 = setup_user(org=self.org_1)
        self.user_2 = setup_user(
            org=self.org_1, email=tv.USER2_EMAIL, password=tv.USER2_PASS
        )
        self.user_3 = setup_user(
            org=self.org_2, email=tv.USER3_EMAIL, password=tv.USER3_PASS
        )
        self.user_1_codes_1 = ["AA1222", "AA1223"]
        self.user_1_codes_2 = ["BB1222", "BB1223"]
        self.user_2_codes = ["CC1222", "CC1223"]
        self.user_1_static_device_1 = setup_2fa_static_device(
            self.user_1, "user1 valid token set 1", codes_list=self.user_1_codes_1
        )
        self.user_1_static_device_2 = setup_2fa_static_device(
            self.user_1, "user1 valid token set 2", codes_list=self.user_1_codes_2
        )
        # invalid set with no codes left
        self.user_1_static_device_3 = setup_2fa_static_device(
            self.user_1, "user1 invalid token set 3"
        )
        self.user_2_static_device_1 = setup_2fa_static_device(
            self.user_2, "user2 valid token set", codes_list=self.user_2_codes
        )

    def test_form_render_only_valid_choices(self):
        form = StaticDeviceCheckForm(self.user_1)
        self.assertIn("user1 valid token set", form.as_p())
        self.assertNotIn("user1 invalid token set", form.as_p())
        self.assertNotIn("user2 valid token set", form.as_p())

    def test_form_accept_valid_token(self):
        # User OK token OK set OK
        form = StaticDeviceCheckForm(
            self.user_1,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": self.user_1_codes_1[0],
            },
        )

        self.assertTrue(form.is_valid())

    def test_form_refuse_invalid_token(self):
        # User OK token OK set KO
        form = StaticDeviceCheckForm(
            self.user_1,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_2.id}",
                "otp_token": self.user_1_codes_1[0],
            },
        )

        self.assertFalse(form.is_valid())

        # User OK token KO set OK (fake token)
        form = StaticDeviceCheckForm(
            self.user_1,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": "fakeToken",
            },
        )

        # User OK token KO set OK (valid token of another user)
        form = StaticDeviceCheckForm(
            self.user_1,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": self.user_2_codes[0],
            },
        )

        self.assertFalse(form.is_valid())

        # User KO token OK and set OK (same org)
        form = StaticDeviceCheckForm(
            self.user_2,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": self.user_1_codes_1[0],
            },
        )

        self.assertFalse(form.is_valid())

        # User KO token OK and set OK (other org)
        form = StaticDeviceCheckForm(
            self.user_3,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": self.user_1_codes_1[0],
            },
        )
        self.assertFalse(form.is_valid())

    def test_form_render_error(self):
        # User OK token KO set OK (fake token)
        form = StaticDeviceCheckForm(
            self.user_1,
            data={
                "otp_device": f"otp_static.staticdevice/{self.user_1_static_device_1.id}",
                "otp_token": "fakeToken",
            },
        )
        self.assertIn("Invalid token", form.as_p())


class TOTPDeviceCheckFormTests(TestCase):
    def setUp(self):
        self.org_1 = setup_org()
        self.org_2 = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        self.user_1 = setup_user(org=self.org_1)
        self.user_2 = setup_user(
            org=self.org_1, email=tv.USER2_EMAIL, password=tv.USER2_PASS
        )
        self.user_1_codes_1 = ["AA1222", "AA1223"]
        self.user_1_static_device_1 = setup_2fa_static_device(
            self.user_1, "user1 valid token set 1", codes_list=self.user_1_codes_1
        )
        self.user_1_fido2_device_1 = setup_2fa_fido2_device(
            self.user_1, "user1 fido2 device 1"
        )
        self.user_1_totp_device_1 = setup_2fa_totp_device(self.user_1, "user1 totp 1")
        self.user_1_totp_device_2 = setup_2fa_totp_device(self.user_1, "user1 totp 2")
        self.user_2_totp_device_2 = setup_2fa_totp_device(self.user_2, "user2 totp 1")

    def test_form_render_only_valid_totp_choices(self):
        form = TOTPDeviceCheckForm(self.user_1)
        self.assertIn("user1 totp 1", form.as_p())
        self.assertIn("user1 totp 2", form.as_p())
        self.assertNotIn("user1 valid token set 1", form.as_p())
        self.assertNotIn("user2 totp 1", form.as_p())
        self.assertNotIn("user1 fido2 device 1", form.as_p())


class StaticDeviceFormTests(TestCase):
    def setUp(self):
        self.org_1 = setup_org()
        self.user_1 = setup_user(org=self.org_1)
        self.user_1_static_device_1 = setup_2fa_static_device(
            self.user_1, tv.STATIC_DEVICE_NAME, codes_list=tv.STATIC_DEVICE_CODES_LIST
        )

    @patch.object(StaticToken, "random_token")
    def test_form_save_proper_model(self, random_token_mock):
        random_token_mock.side_effect = tv.STATIC_DEVICE_CODES_LIST
        expected_model = self.user_1_static_device_1

        form = StaticDeviceForm(data={"name": tv.STATIC_DEVICE_NAME})

        self.assertTrue(form.is_valid())

        saved_model = form.save(self.user_1)

        self.assertEqual(expected_model.name, saved_model.name)
        self.assertCountEqual(
            StaticToken.objects.filter(device_id=expected_model.id).values_list(
                "token", flat=True
            ),
            StaticToken.objects.filter(device_id=saved_model.id).values_list(
                "token", flat=True
            ),
        )


class TOTPDeviceFormTests(TestCase):
    def setUp(self):
        self.org_1 = setup_org()
        self.user_1 = setup_user(org=self.org_1)
        self.user_1_totp_device_1 = setup_2fa_totp_device(
            self.user_1, "user1 totp 1", confirmed=False
        )

    @patch("django_otp.plugins.otp_totp.models.random_hex")
    def test_form_save_proper_model(self, random_hex_mock):
        random_hex_mock.return_value = tv.TOTP_DEVICE_SECRET_KEY
        expected_model = setup_2fa_totp_device(
            self.user_1, tv.TOTP_DEVICE_NAME, secret_key=tv.TOTP_DEVICE_SECRET_KEY
        )
        form = TOTPDeviceForm(data={"name": tv.TOTP_DEVICE_NAME})

        self.assertTrue(form.is_valid())

        saved_model = form.save(self.user_1)

        self.assertEqual(expected_model.name, saved_model.name)
        self.assertEqual(expected_model.key, saved_model.key)


class TOTPDeviceConfirmFormTests(TestCase):
    def setUp(self):
        self.org_1 = setup_org()
        self.user_1 = setup_user(org=self.org_1)
        self.user_1_totp_device_1 = setup_2fa_totp_device(
            self.user_1, "user1 totp 1", confirmed=False
        )

    @patch("django_otp.plugins.otp_totp.models.random_hex")
    def test_form_save_proper_model(self, random_hex_mock):
        random_hex_mock.return_value = tv.TOTP_DEVICE_SECRET_KEY
        expected_model = setup_2fa_totp_device(
            self.user_1, tv.TOTP_DEVICE_NAME, secret_key=tv.TOTP_DEVICE_SECRET_KEY
        )
        form = TOTPDeviceForm(data={"name": tv.TOTP_DEVICE_NAME})

        self.assertTrue(form.is_valid())

        saved_model = form.save(self.user_1)

        self.assertEqual(expected_model.name, saved_model.name)
        self.assertEqual(expected_model.key, saved_model.key)
