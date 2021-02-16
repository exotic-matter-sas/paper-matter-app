#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import re
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock, call

import qrcode.image.svg
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.backends.base import SessionBase
from django.test import RequestFactory, override_settings
from django.test import TestCase
from django.urls import reverse_lazy, reverse
from django.utils import timezone as django_timezone
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_registration.backends.activation.views import RegistrationView
from rest_framework import status

from core.models import FTLUser
from ftests.test_account import (
    totp_time_setter,
    totp_time_property,
    mocked_totp_time_setter,
    mocked_verify_user,
)
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
    setup_2fa_totp_device,
    setup_2fa_static_device,
    setup_2fa_fido2_device,
)
from ftests.tools.test_values import TOTP_DEVICE_SECRET_KEY, TOTP_DEVICE_VALID_TOKEN
from ftl import celery
from ftl.otp_plugins.otp_ftl.forms import TOTPDeviceConfirmForm
from ftl.otp_plugins.otp_ftl.models import Fido2Device
from ftl.otp_plugins.otp_ftl.views_fido2 import Fido2Check
from ftl.otp_plugins.otp_ftl.views_static import StaticDeviceCheck, StaticDeviceAdd
from ftl.otp_plugins.otp_ftl.views_totp import (
    TOTPDeviceCheck,
    TOTPDeviceAdd,
    TOTPDeviceConfirm,
)


class FtlPagesTests(TestCase):
    def test_index_redirects(self):
        """Index redirect to correct page according to setup state"""
        response = self.client.get("", follow=True)
        self.assertRedirects(response, reverse_lazy("setup:create_admin"))

        org = setup_org()
        setup_admin(org)
        response = self.client.get("", follow=True)
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('home')}"
        )

    def test_signup_returns_correct_html(self):
        """Signup page returns correct html"""
        response = self.client.get("/signup/")
        self.assertContains(response, "Create your account")
        self.assertTemplateUsed(
            response, "ftl/registration/create_org_and_ftluser.html"
        )

    @patch.object(celery.app, "send_task")
    def test_signup_get_success_url(self, mocked_send_email_async):
        response = self.client.post(
            "/signup/",
            {
                "org_name": tv.ORG_NAME_1,
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
            },
        )
        self.assertRedirects(
            response, reverse_lazy("signup_success"), fetch_redirect_response=False
        )

    def test_signup_success_returns_correct_html(self):
        """Signup success page returns correct html"""

        response = self.client.get(f"/signup/success/")
        self.assertContains(response, "verify your email")
        self.assertTemplateUsed(response, "ftl/registration/signup_success.html")

    @override_settings(FTL_ENABLE_SIGNUP_CAPTCHA=True)
    @patch.object(celery.app, "send_task")
    def test_signup_with_captcha(self, mocked_send_email_async):
        # Generate at least one captcha
        response = self.client.get(reverse("signup_org_user"))
        # Retrieve hash and expected captcha value from DB
        hash_ = re.findall(r'value="([0-9a-f]+)"', str(response.content))[0]
        self.assertIsNotNone(hash_)
        captcha_response = CaptchaStore.objects.get(hashkey=hash_).response
        self.assertIsNotNone(captcha_response)

        response_submit = self.client.post(
            reverse("signup_org_user"),
            {
                "org_name": tv.ORG_NAME_1,
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
                "captcha_0": hash_,
                "captcha_1": captcha_response,
            },
        )

        self.assertRedirects(
            response_submit,
            reverse_lazy("signup_success"),
            fetch_redirect_response=False,
        )

    @override_settings(FTL_ENABLE_SIGNUP_CAPTCHA=True)
    @patch.object(celery.app, "send_task")
    def test_signup_with_wrong_captcha(self, mocked_send_email_async):
        # Generate at least one captcha
        response = self.client.get(reverse("signup_org_user"))
        # Retrieve hash
        hash_ = re.findall(r'value="([0-9a-f]+)"', str(response.content))[0]

        response_submit = self.client.post(
            reverse("signup_org_user"),
            {
                "org_name": tv.ORG_NAME_1,
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
                "captcha_0": hash_,
                "captcha_1": "wrong captcha",
            },
        )

        self.assertFalse(response_submit.context_data["form"].is_valid())
        self.assertIn("captcha", response_submit.context_data["form"].errors)

    @patch.object(celery.app, "send_task")
    def test_user_permissions_signup(self, mocked_send_email_async):
        self.client.post(
            "/signup/",
            {
                "org_name": tv.ORG_NAME_1,
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
            },
        )

        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        self.assertIsNotNone(user)

        # To test permission, we need an account activated otherwise the permissions are not set
        registration_view = RegistrationView()
        activation_key = registration_view.get_activation_key(user)

        response = self.client.get(f"/accounts/activate/{activation_key}/", follow=True)
        self.assertEqual(response.status_code, 200)
        # Not tested for now
        # user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        # self.assertTrue(user.has_perms(FTL_PERMISSIONS_USER))

    @patch.object(user_logged_out, "send")
    def test_logout_call_proper_signal(self, mocked_signal):
        # Setup org, admin, user and log the user
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        setup_authenticated_session(self.client, org, user)

        self.client.get("/logout/")

        mocked_signal.assert_called_once()

    @patch.object(messages, "success")
    def test_logout_signal_trigger_django_messages(self, messages_mocked):
        # Setup org, admin, user and log the user
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        setup_authenticated_session(self.client, org, user)

        message_to_display_on_login_page = "bingo!"
        messages_mocked.return_value = message_to_display_on_login_page
        mocked_request = Mock()
        mocked_request.GET = {}
        mocked_request.axes_attempt_time = datetime.now()
        user_logged_out.send(self.__class__, request=mocked_request, user=user)

        messages_mocked.assert_called_once()


########################
# Otp_ftl plugin views #
########################


class OTPCheckViewTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and user is logged
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)
        # reset mock
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    @patch.object(TOTP, "time", totp_time_property)
    def test_session_timeout_reduced_during_2fa_check(self):
        totp_device = setup_2fa_totp_device(
            self.user, secret_key=TOTP_DEVICE_SECRET_KEY
        )
        totp_time_setter.side_effect = mocked_totp_time_setter

        self.client.get("/app/", follow=True)

        # During 2fa session duration must be less than 10 mins
        now = datetime.now(timezone.utc)
        cookie_expiration_time = self.client.cookies["sessionid"]["expires"]
        cookie_expiration_time = datetime.strptime(
            cookie_expiration_time, "%a, %d %b %Y %H:%M:%S GMT"
        )
        cookie_expiration_time = django_timezone.make_aware(
            cookie_expiration_time, timezone.utc
        )
        delta = cookie_expiration_time - now
        self.assertLessEqual(delta, timedelta(minutes=10))

        self.client.post(
            "/accounts/2fa/totp/check/",
            {
                "otp_device": totp_device.persistent_id,
                "otp_token": TOTP_DEVICE_VALID_TOKEN,
            },
            follow=True,
        )

        # After 2FA check session have to be restore to default value
        cookie_expiration_time = self.client.cookies["sessionid"]["expires"]
        cookie_expiration_time = datetime.strptime(
            cookie_expiration_time, "%a, %d %b %Y %H:%M:%S GMT"
        )
        cookie_expiration_time = django_timezone.make_aware(
            cookie_expiration_time, timezone.utc
        )
        delta = cookie_expiration_time - now

        self.assertAlmostEqual(
            round(delta.total_seconds()), settings.SESSION_COOKIE_AGE, delta=5
        )

    def test_otp_check_redirect_to_proper_view(self):
        # Given no 2fa devices are setup
        response = self.client.get("/app/")
        # Home page is displayed
        self.assertTemplateUsed(response, "core/home.html")

        # Given a static device is setup
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(response, reverse_lazy("otp_static_check"))

        # Given static + totp device are setup
        setup_2fa_totp_device(self.user)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(response, reverse_lazy("otp_totp_check"))

        # Given static + totp + 2fa device are setup
        setup_2fa_fido2_device(self.user)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(response, reverse_lazy("otp_fido2_check"))


class OTPFtlViewsTests(TestCase):
    def setUp(self):
        # Setup org, user
        self.org = setup_org()
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_list_returns_correct_html(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # Given no 2fa devices are setup
        response = self.client.get("/accounts/2fa/")
        self.assertContains(response, "Protect your Paper Matter account")
        self.assertTemplateUsed(response, "otp_ftl/device_list.html")

        # Given 2fa devices are setup
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)
        setup_2fa_fido2_device(self.user)
        setup_2fa_totp_device(self.user)

        response = self.client.get("/accounts/2fa/")
        self.assertContains(response, "Emergency codes")
        self.assertContains(response, "Security keys (U2F/FIDO2)")
        self.assertContains(response, "Authenticator apps")

    def test_otp_list_context(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # Given 2fa devices are setup
        static_device_1 = setup_2fa_static_device(
            self.user, "SD1", codes_list=tv.STATIC_DEVICE_CODES_LIST
        )
        static_device_2 = setup_2fa_static_device(
            self.user, "SD2", codes_list=tv.STATIC_DEVICE_CODES_LIST
        )
        totp_device_1 = setup_2fa_totp_device(self.user, "TD1")
        totp_device_2 = setup_2fa_totp_device(self.user, "TD2")
        fido2_device_1 = setup_2fa_fido2_device(self.user, "FD1")
        fido2_device_2 = setup_2fa_fido2_device(self.user, "FD2")

        response = self.client.get("/accounts/2fa/")

        self.assertCountEqual(
            response.context["static_devices"], [static_device_1, static_device_2]
        )
        self.assertCountEqual(
            response.context["totp_devices"], [totp_device_1, totp_device_2]
        )
        self.assertCountEqual(
            response.context["fido2_devices"], [fido2_device_1, fido2_device_2]
        )


class OTPFtlViewsStaticTests(TestCase):
    def setUp(self):
        # Setup org, user, a static device and the user is logged
        self.org = setup_org()
        self.user = setup_user(self.org)
        self.static_device = setup_2fa_static_device(
            self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST
        )
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_static_check_returns_correct_html(self):
        response = self.client.get("/accounts/2fa/static/check/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_check.html")

    def test_otp_static_check_context(self):
        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], False)
        self.assertEqual(response.context["have_totp"], False)

        # given user setup static + fido2 devices
        setup_2fa_fido2_device(self.user)

        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], False)
        # given user setup static + fido2 + totp devices
        setup_2fa_totp_device(self.user)

        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], True)

    def test_otp_static_check_success_url(self):
        # Given there is no next querystring set
        request_factory = RequestFactory()
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set to Home
        self.assertEqual(otp_static_check_view.get_success_url(), reverse_lazy("home"))

        # Given there is a safe url in next querystring
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = reverse_lazy("account_index")

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set to next url
        self.assertEqual(
            otp_static_check_view.get_success_url(), reverse_lazy("account_index")
        )

        # Given there is an unsafe url in next querystring
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = "https://buymybitcoins.plz"

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set NOT set to next url, it defaults to Home
        self.assertEqual(otp_static_check_view.get_success_url(), reverse_lazy("home"))

    def test_otp_static_detail_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/{self.static_device.id}/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_detail.html")

    def test_otp_static_update_returns_correct_html(self):
        response = self.client.get(
            f"/accounts/2fa/static/{self.static_device.id}/update/"
        )

        self.assertTemplateUsed(response, "otp_ftl/device_update.html")

    def test_otp_static_add_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_form.html")

    def test_otp_static_add_get_success_url(self):
        response = self.client.post(
            f"/accounts/2fa/static/", data={"name": tv.STATIC_DEVICE_NAME}
        )

        # get_success_url redirect to the detail of the static device just created
        self.assertRedirects(
            response,
            reverse_lazy(
                "otp_static_detail", kwargs={"pk": StaticDevice.objects.last().id}
            ),
        )

    def test_otp_static_add_form_valid_set_data(self):
        request_factory = RequestFactory()
        request = request_factory.post(
            "/accounts/2fa/static/", {"name": tv.STATIC_DEVICE_NAME}
        )
        request.user = self.user

        otp_static_add_view = StaticDeviceAdd()
        otp_static_add_view.request = request
        form = otp_static_add_view.get_form(otp_static_add_view.form_class)
        form.is_valid()
        otp_static_add_view.form_valid(form)

        # instance attribute is populate the model of the static device just created
        self.assertEqual(otp_static_add_view.instance, StaticDevice.objects.last())

    def test_otp_static_delete_returns_correct_html(self):
        response = self.client.get(
            f"/accounts/2fa/static/{self.static_device.id}/delete/"
        )

        self.assertTemplateUsed(response, "otp_ftl/device_confirm_delete.html")


class OTPFtlViewsTOTPTests(TestCase):
    def setUp(self):
        # Setup org, user, a totp device and the user is logged
        self.org = setup_org()
        self.user = setup_user(self.org)
        self.totp_device = setup_2fa_totp_device(self.user, confirmed=False)
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_totp_check_returns_correct_html(self):
        response = self.client.get("/accounts/2fa/totp/check/")

        self.assertTemplateUsed(response, "otp_ftl/totpdevice_check.html")

    def test_otp_totp_check_context(self):
        # given user have confirmed is totp device
        self.totp_device.confirmed = True
        self.totp_device.save()
        response = self.client.get("/accounts/2fa/totp/check/")

        self.assertEqual(response.context["have_totp"], True)
        self.assertEqual(response.context["have_fido2"], False)
        self.assertEqual(response.context["have_static"], False)

        # given user setup totp + fido2 devices
        setup_2fa_fido2_device(self.user)

        response = self.client.get("/accounts/2fa/totp/check/")

        self.assertEqual(response.context["have_totp"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_static"], False)
        # given user setup static + fido2 + totp devices
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)

        response = self.client.get("/accounts/2fa/totp/check/")

        self.assertEqual(response.context["have_totp"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_static"], True)

    def test_otp_totp_check_success_url(self):
        # Given there is no next querystring set
        request_factory = RequestFactory()
        request = request_factory.get("/accounts/2fa/totp/check/")
        request.user = self.user
        request.session = SessionBase()

        otp_totp_check_view = TOTPDeviceCheck()
        otp_totp_check_view.request = request

        # Success url is set to Home
        self.assertEqual(otp_totp_check_view.get_success_url(), reverse_lazy("home"))

        # Given there is a safe url in next querystring
        request = request_factory.get("/accounts/2fa/totp/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = reverse_lazy("account_index")

        otp_totp_check_view = TOTPDeviceCheck()
        otp_totp_check_view.request = request

        # Success url is set to next url
        self.assertEqual(
            otp_totp_check_view.get_success_url(), reverse_lazy("account_index")
        )

        # Given there is an unsafe url in next querystring
        request = request_factory.get("/accounts/2fa/totp/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = "https://buymybitcoins.plz"

        otp_totp_check_view = TOTPDeviceCheck()
        otp_totp_check_view.request = request

        # Success url is set NOT set to next url, it defaults to Home
        self.assertEqual(otp_totp_check_view.get_success_url(), reverse_lazy("home"))

    def test_otp_totp_update_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/update/")

        self.assertTemplateUsed(response, "otp_ftl/device_update.html")

    def test_otp_totp_add_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/totp/")

        self.assertTemplateUsed(response, "otp_ftl/totpdevice_form.html")

    def test_otp_totp_add_get_success_url(self):
        response = self.client.post(
            f"/accounts/2fa/totp/", data={"name": tv.STATIC_DEVICE_NAME}
        )

        # get_success_url redirect to the detail of the totp device just created
        self.assertRedirects(
            response,
            reverse_lazy(
                "otp_totp_detail", kwargs={"pk": TOTPDevice.objects.last().id}
            ),
        )

    def test_otp_totp_add_form_valid_set_data(self):
        request_factory = RequestFactory()
        request = request_factory.post(
            "/accounts/2fa/totp/", {"name": tv.TOTP_DEVICE_NAME}
        )
        request.user = self.user

        otp_totp_add_view = TOTPDeviceAdd()
        otp_totp_add_view.request = request
        form = otp_totp_add_view.get_form(otp_totp_add_view.form_class)
        form.is_valid()
        otp_totp_add_view.form_valid(form)

        # instance attribute is populate the model of the totp device just created
        self.assertEqual(otp_totp_add_view.instance, TOTPDevice.objects.last())

    def test_otp_totp_delete_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/delete/")

        self.assertTemplateUsed(response, "otp_ftl/device_confirm_delete.html")

    def test_otp_static_delete_context(self):
        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/delete/")

        self.assertEqual(response.context["last_otp"], True)

        # given user add a totp device
        totp_device_2 = setup_2fa_totp_device(self.user)

        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/delete/")

        self.assertEqual(response.context["last_otp"], False)

        # given delete second totp device and add a fido2 device
        totp_device_2.delete()
        setup_2fa_fido2_device(self.user)

        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/delete/")

        self.assertEqual(response.context["last_otp"], False)

    def test_otp_totp_display_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/")

        self.assertTemplateUsed(response, "otp_ftl/totpdevice_detail.html")

    def test_otp_totp_display_context(self):
        response = self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/")

        self.assertIsInstance(response.context["form"], TOTPDeviceConfirmForm)

    def test_otp_totp_confirm_returns_correct_html(self):
        response = self.client.post(f"/accounts/2fa/totp/{self.totp_device.id}/")

        self.assertTemplateUsed(response, "otp_ftl/totpdevice_detail.html")

    def test_otp_totp_confirm_success_url(self):
        # Given user didn't set static device
        request_factory = RequestFactory()
        request = request_factory.post(f"/accounts/2fa/totp/{self.totp_device.id}/")
        request.user = self.user
        request.session = SessionBase()

        otp_totp_confirm_view = TOTPDeviceConfirm()
        otp_totp_confirm_view.request = request

        # Success url is set to otp_static_add
        self.assertEqual(
            otp_totp_confirm_view.get_success_url(), reverse_lazy("otp_static_add")
        )

        # Given user set one static device
        setup_2fa_static_device(self.user)
        request = request_factory.post(f"/accounts/2fa/totp/{self.totp_device.id}/")
        request.user = self.user

        otp_totp_confirm_view = TOTPDeviceConfirm()
        otp_totp_confirm_view.request = request

        # Success url is set to otp_list
        self.assertEqual(
            otp_totp_confirm_view.get_success_url(), reverse_lazy("otp_list")
        )

        # Given user set two static devices
        setup_2fa_static_device(self.user)
        request = request_factory.post(f"/accounts/2fa/totp/{self.totp_device.id}/")
        request.user = self.user

        otp_totp_confirm_view = TOTPDeviceConfirm()
        otp_totp_confirm_view.request = request

        # Success url is set to otp_list
        self.assertEqual(
            otp_totp_confirm_view.get_success_url(), reverse_lazy("otp_list")
        )

    def test_otp_totp_confirm_get_form_kwargs(self):
        # Given post method have been called
        request_factory = RequestFactory()
        request = request_factory.post(f"/accounts/2fa/totp/{self.totp_device.id}/")
        request.user = self.user

        otp_totp_confirm_view = TOTPDeviceConfirm()
        otp_totp_confirm_view.request = request
        TOTPDeviceConfirm.setup(
            otp_totp_confirm_view, request, pk=self.totp_device.id
        )  # to init self.kwargs
        otp_totp_confirm_view.post(request)  # to set self.object

        # get_form_kwargs add data to form kwargs
        kwargs = otp_totp_confirm_view.get_form_kwargs()
        self.assertEqual(kwargs["user"], self.user)
        self.assertEqual(kwargs["request"], request)
        self.assertEqual(kwargs["device"], self.totp_device)

    def test_otp_totp_confirm_form_valid_set_data(self):
        request_factory = RequestFactory()
        request = request_factory.post(f"/accounts/2fa/totp/{self.totp_device.id}/")
        request.user = self.user
        request.session = SessionBase()
        # mock session create method because it is required by form_valid of parent view (login call)
        request.session.create = lambda: True

        otp_totp_confirm_view = TOTPDeviceConfirm()
        TOTPDeviceConfirm.setup(
            otp_totp_confirm_view, request, pk=self.totp_device.id
        )  # to init self.kwargs
        otp_totp_confirm_view.post(request)  # to set self.object
        otp_totp_confirm_view.request = request
        form = otp_totp_confirm_view.get_form(otp_totp_confirm_view.form_class)
        form.is_valid()
        otp_totp_confirm_view.form_valid(form)

        # Device is saved with confirmed attribute set to True
        expected_device = TOTPDevice.objects.get(pk=self.totp_device.id)
        self.assertEqual(expected_device.confirmed, True)

    @patch("ftl.otp_plugins.otp_ftl.views_totp.qrcode.make")
    def test_otp_totp_qrcode_call_qrcode_make(self, mocked_make):
        self.client.get(f"/accounts/2fa/totp/{self.totp_device.id}/qrcode/")

        mocked_make.assert_called_once_with(
            self.totp_device.config_url, image_factory=qrcode.image.svg.SvgImage
        )


class OTPFtlViewsFido2Tests(TestCase):
    def setUp(self):
        # Setup org, user, a fido2 device and the user is logged
        self.org = setup_org()
        self.user = setup_user(self.org)
        self.fido2_device = setup_2fa_fido2_device(self.user)
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_fido2_check_returns_correct_html(self):
        response = self.client.get("/accounts/2fa/fido2/check/")

        self.assertTemplateUsed(response, "otp_ftl/fido2device_check.html")

    def test_otp_fido2_check_context(self):
        response = self.client.get("/accounts/2fa/fido2/check/")

        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], False)
        self.assertEqual(response.context["have_static"], False)

        # given user setup totp + fido2 devices
        setup_2fa_totp_device(self.user)

        response = self.client.get("/accounts/2fa/fido2/check/")

        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], True)
        self.assertEqual(response.context["have_static"], False)
        # given user setup static + fido2 + totp devices
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)

        response = self.client.get("/accounts/2fa/fido2/check/")

        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], True)
        self.assertEqual(response.context["have_static"], True)

    def test_otp_fido2_check_success_url(self):
        # Given there is no next querystring set
        request_factory = RequestFactory()
        request = request_factory.get("/accounts/2fa/fido2/check/")
        request.user = self.user
        request.session = SessionBase()

        otp_fido2_check_view = Fido2Check()
        otp_fido2_check_view.request = request

        # Success url is set to Home
        self.assertEqual(otp_fido2_check_view.get_success_url(), reverse_lazy("home"))

        # Given there is a safe url in next querystring
        request = request_factory.get("/accounts/2fa/fido2/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = reverse_lazy("account_index")

        otp_fido2_check_view = Fido2Check()
        otp_fido2_check_view.request = request

        # Success url is set to next url
        self.assertEqual(
            otp_fido2_check_view.get_success_url(), reverse_lazy("account_index")
        )

        # Given there is an unsafe url in next querystring
        request = request_factory.get("/accounts/2fa/fido2/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = "https://buymybitcoins.plz"

        otp_fido2_check_view = Fido2Check()
        otp_fido2_check_view.request = request

        # Success url is set NOT set to next url, it defaults to Home
        self.assertEqual(otp_fido2_check_view.get_success_url(), reverse_lazy("home"))

    def test_otp_fido2_update_returns_correct_html(self):
        response = self.client.get(
            f"/accounts/2fa/fido2/{self.fido2_device.id}/update/"
        )

        self.assertTemplateUsed(response, "otp_ftl/device_update.html")

    def test_otp_fido2_add_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/fido2/")

        self.assertTemplateUsed(response, "otp_ftl/fido2device_form.html")

    def test_otp_fido2_delete_returns_correct_html(self):
        response = self.client.get(
            f"/accounts/2fa/fido2/{self.fido2_device.id}/delete/"
        )

        self.assertTemplateUsed(response, "otp_ftl/device_confirm_delete.html")

    def test_otp_fido2_success_returns_correct_html(self):
        response = self.client.get("/accounts/2fa/fido2/success/")

        self.assertTemplateUsed(response, "otp_ftl/fido2device_detail.html")

    @patch("ftl.otp_plugins.otp_ftl.views_fido2.AttestedCredentialData")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.cbor2")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.PublicKeyCredentialRpEntity")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.Fido2Server")
    def test_otp_fido2_api_register_begin(
        self, fido2_server_mock, pkcre_mock, cbor2_mock, acd_mock
    ):
        # given user setup another fido2_device
        fido2_device_2 = setup_2fa_fido2_device(self.user, name="second fido device")

        register_begin_return_value = ["fake_registration_data", "fake_state"]
        fido2_server_mock().register_begin.return_value = register_begin_return_value
        fido2_server_mock.reset_mock()  # previous assignment count as a call so we need to reset mock counter
        fake_credentials_list = ["fake_credential_1", "fake_credential_2°"]
        acd_mock.side_effect = fake_credentials_list
        fake_cbor2_loaded_list = ["fake_cbor2_loaded_1", "fake_cbor2_loaded_2"]
        cbor2_mock.loads.side_effect = fake_cbor2_loaded_list
        cbor2_mock.dumps.return_value = b"fake_registration_data"

        response = self.client.get("/accounts/2fa/fido2/api/register_begin")

        pkcre_mock.assert_called_once_with("testserver", settings.FIDO2_RP_NAME)
        fido2_server_mock.assert_called_once_with(pkcre_mock())

        self.assertEqual(cbor2_mock.loads.call_count, 2)
        _, loads_mock_first_call_args, _ = cbor2_mock.loads.mock_calls[0]
        _, loads_mock_second_call_args, _ = cbor2_mock.loads.mock_calls[1]
        self.assertEqual(
            loads_mock_first_call_args[0].tobytes(),
            self.fido2_device.authenticator_data,
        )
        self.assertEqual(
            loads_mock_second_call_args[0].tobytes(), fido2_device_2.authenticator_data
        )

        fido2_server_mock().register_begin.assert_called_once_with(
            {
                "id": self.user.email.encode(),
                "name": self.user.email,
                "displayName": self.user.email,
                "icon": "",
            },
            credentials=fake_credentials_list,
            user_verification="discouraged",
            authenticator_attachment="cross-platform",
        )

        cbor2_mock.dumps.assert_called_once_with(register_begin_return_value[0])

        self.assertEqual(
            response.wsgi_request.session.get("fido2_register_state"),
            register_begin_return_value[1],
        )

        self.assertEqual(response.content, cbor2_mock.dumps.return_value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/octet-stream")

    @patch("ftl.otp_plugins.otp_ftl.views_fido2.Fido2Server")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.PublicKeyCredentialRpEntity")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.AttestationObject")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.ClientData")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.cbor2")
    def test_otp_fido2_api_register_finish(
        self,
        cbor2_mock,
        client_data_mock,
        attestation_object_mock,
        pkcre_mock,
        fido2_server_mock,
    ):
        device_name = "Fido2 device just added"
        fake_cbor2_loads_value = {
            "name": device_name,
            "clientDataJSON": "fakeClientDataJSON",
            "attestationObject": "fakeattestationObject",
        }
        cbor2_mock.loads.return_value = fake_cbor2_loads_value
        cbor2_mock.dumps.return_value = b"fake_authenticator_data"
        session = self.client.session
        session["fido2_register_state"] = "fake_registration_data"
        session.save()
        client_data_mock.return_value = "fake_client_data"
        attestation_object_mock.return_value = "fake_attestation_object"

        response = self.client.get("/accounts/2fa/fido2/api/register_finish")

        cbor2_mock.loads.assert_called_once_with(response.wsgi_request.body)
        client_data_mock.assert_called_once_with(
            fake_cbor2_loads_value["clientDataJSON"]
        )
        attestation_object_mock.assert_called_once_with(
            fake_cbor2_loads_value["attestationObject"]
        )

        pkcre_mock.assert_called_once_with("testserver", settings.FIDO2_RP_NAME)
        fido2_server_mock().register_complete.assert_called_once_with(
            "fake_registration_data",
            client_data_mock.return_value,
            attestation_object_mock.return_value,
        )

        self.assertEqual(2, Fido2Device.objects.count())
        self.assertEqual(1, len(Fido2Device.objects.filter(name=device_name)))

        self.assertEqual(response.content, cbor2_mock.dumps.return_value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/cbor")

    @patch("ftl.otp_plugins.otp_ftl.views_fido2.Fido2Server")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.PublicKeyCredentialRpEntity")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.cbor2")
    @patch("ftl.otp_plugins.otp_ftl.views_fido2.AttestedCredentialData")
    def test_otp_fido2_api_login_begin(
        self, acd_mock, cbor2_mock, pkcre_mock, fido2_server_mock
    ):
        # given user setup another fido2_device
        setup_2fa_fido2_device(self.user, name="second fido device")

        authenticate_begin_return_value = ["fake_auth_data", "fake_state"]
        fido2_server_mock().authenticate_begin.return_value = (
            authenticate_begin_return_value
        )
        fido2_server_mock.reset_mock()  # previous assignment count as a call so we need to reset mock counter
        fake_credentials_list = ["fake_credential_1", "fake_credential_2"]
        acd_mock.side_effect = fake_credentials_list
        fake_cbor2_loaded_list = ["fake_cbor2_loaded_1", "fake_cbor2_loaded_2"]
        cbor2_mock.loads.side_effect = fake_cbor2_loaded_list
        cbor2_mock.dumps.return_value = b"fakeAuthData"

        response = self.client.get("/accounts/2fa/fido2/api/login_begin")

        self.assertEqual(acd_mock.call_count, 2)
        acd_mock.assert_any_call(fake_cbor2_loaded_list[0])
        acd_mock.assert_any_call(fake_cbor2_loaded_list[1])

        pkcre_mock.assert_called_once_with("testserver", settings.FIDO2_RP_NAME)
        fido2_server_mock.assert_called_once_with(pkcre_mock())

        fido2_server_mock().authenticate_begin.assert_called_once_with(
            fake_credentials_list, user_verification="discouraged",
        )

        self.assertEqual(
            response.wsgi_request.session.get("fido2_state"),
            authenticate_begin_return_value[1],
        )
        self.assertEqual(
            response.wsgi_request.session.get("fido2_domain"), "testserver"
        )

        cbor2_mock.dumps.assert_called_once_with(authenticate_begin_return_value[0])

        self.assertEqual(response.content, cbor2_mock.dumps.return_value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/cbor")
