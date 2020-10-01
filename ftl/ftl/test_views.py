#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from datetime import datetime
from unittest.mock import patch, Mock

from django.contrib import messages
from django.contrib.auth.signals import user_logged_out
from django.test import TestCase
from django.urls import reverse_lazy
from django_registration.backends.activation.views import RegistrationView

from core.models import FTLUser, FTL_PERMISSIONS_USER
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
)
from ftl import celery


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
        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        self.assertTrue(user.has_perms(FTL_PERMISSIONS_USER))

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
