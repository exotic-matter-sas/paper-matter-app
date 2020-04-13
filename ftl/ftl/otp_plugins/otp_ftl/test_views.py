from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from django.conf.global_settings import SESSION_COOKIE_AGE
from django.test import TestCase
from django.utils import timezone as django_timezone
from django_otp.oath import TOTP

from ftests.test_account import (
    TotpDevice2FATests,
    totp_time_property,
    totp_time_setter,
    mocked_totp_time_setter,
)
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
    setup_2fa_totp_device,
)


class TwoFaCheckPagesTests(TestCase):
    def setUp(self):
        # Setup org, admin, user, 2fa totp device already setup and user is logged
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.totp_device = setup_2fa_totp_device(
            self.user, secret_key=TotpDevice2FATests.secret_key
        )
        setup_authenticated_session(self.client, self.org, self.user)
        # reset mock
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    @patch.object(TOTP, "time", totp_time_property)
    def test_session_timeout_reduced_during_2fa_check(self):
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
            "/accounts/2fa/totp/check",
            {
                "otp_device": self.totp_device.persistent_id,
                "otp_token": TotpDevice2FATests.valid_token,
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

        self.assertEqual(round(delta.total_seconds()), SESSION_COOKIE_AGE)
