#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for license information.
from dateutil.tz import gettz
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone, dateformat, translation
from django.utils.formats import get_format

from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_authenticated_session,
)


class TestFTLLanguageMiddleware(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        self.admin = setup_admin(self.org)

    def test_no_language_configured_use_browser_accept_language(self):
        self.admin.lang = ""
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        response = self.client.get(
            reverse_lazy("account_index"), HTTP_ACCEPT_LANGUAGE="fr"
        )

        self.assertContains(response, "Paramètres")
        self.assertIn("content-language", response)
        self.assertEqual("fr", response["content-language"])

    def test_activate_language_fr(self):
        self.admin.lang = "fr"
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        response = self.client.get(reverse_lazy("account_index"))

        self.assertContains(response, "Paramètres")
        self.assertIn("content-language", response)
        self.assertEqual("fr", response["content-language"])

    def test_activate_language_en(self):
        self.admin.lang = "en"
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        response = self.client.get(reverse_lazy("account_index"))

        self.assertContains(response, "Settings")
        self.assertIn("content-language", response)
        self.assertEqual("en", response["content-language"])

    def test_activate_language_en_with_fr_browser(self):
        self.admin.lang = "en"
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        response = self.client.get(
            reverse_lazy("account_index"), HTTP_ACCEPT_LANGUAGE="fr"
        )

        self.assertContains(response, "Settings")
        self.assertIn("content-language", response)
        self.assertEqual("en", response["content-language"])


class TestFTLTimezoneMiddleware(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        self.admin = setup_admin(self.org)

    def test_timezone_us_east_cost(self):
        self.admin.lang = "en"
        self.admin.tz = "America/New_York"
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        with translation.override("en"):
            # Force translation to en only in this code block
            now_in_utc = timezone.now()
            now_ny = timezone.localtime(now_in_utc, gettz("America/New_York"))
            # Use Django timezone tool to get the expected time in New York, USA
            formatted = dateformat.format(
                now_ny, get_format("SHORT_DATETIME_FORMAT", lang="en", use_l10n=True)
            )

        response = self.client.get(reverse_lazy("account_user_settings"))
        self.assertContains(response, formatted)

    def test_timezone_fr(self):
        self.admin.lang = "fr"
        self.admin.tz = "Europe/Paris"
        self.admin.save()

        setup_authenticated_session(self.client, self.org, self.admin)

        with translation.override("fr"):
            # Force translation to fr only in this code block
            now_in_utc = timezone.now()
            now_in_paris = timezone.localtime(now_in_utc, gettz("Europe/Paris"))
            # Use Django timezone tool to get the expected time in Paris, FR
            formatted = dateformat.format(
                now_in_paris,
                get_format("SHORT_DATETIME_FORMAT", lang="fr", use_l10n=True),
            )

        response = self.client.get(reverse_lazy("account_user_settings"))
        self.assertContains(response, formatted)
