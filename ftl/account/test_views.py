#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.test import TestCase
from django.urls import reverse

from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
)


class AccountSettingsTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)

    def test_set_language_and_timezone(self):
        response = self.client.post(
            reverse("account_user_settings"),
            data={"lang": "fr", "tz": "Europe/Paris"},
            follow=True,
        )

        self.assertRedirects(response, reverse("account_index"))
        self.assertContains(
            response, "Your settings were saved.",
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.lang, "fr")
        self.assertEqual(self.user.tz, "Europe/Paris")
