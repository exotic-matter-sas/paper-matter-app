#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

import threading

from django.core import mail
from django.test import override_settings

from ftests.pages.account_pages import AccountPages
from ftests.pages.login_page import LoginPage
from ftests.pages.signup_pages import SignupPages
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin
from ftl.celery import app


@override_settings(CELERY_BROKER_URL="memory://localhost")
@override_settings(CELERY_TASK_ROUTES={})
class SignupPageTests(SignupPages):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.control.purge()
        cls._worker = app.Worker(app=app, pool="solo", concurrency=1)
        cls._thread = threading.Thread(target=cls._worker.start)
        cls._thread.daemon = True
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        cls._worker.stop()
        super().tearDownClass()

    def setUp(self, **kwargs):
        # first org and admin already created
        super().setUp()
        self.admin_org = setup_org("admin org", "admin-org")
        setup_admin(org=self.admin_org)

    def test_first_user_signup(self):
        # User create an account in the first org
        self.visit(self.url)
        self.create_user()

        # Success page appears
        self.assertIn(
            "verify your email inbox to activate your account",
            self.get_elem(self.main_panel).text,
        )

    def test_signup_failed(self):
        # User try to create an account without filling fields
        self.visit(self.url)
        self.get_elem(self.submit_input).click()

        # The browser refused form submission as all fields are set to required
        self.assertIn("signup", self.head_title)
        self.assertIn("Create your account", self.get_elem(self.page_title).text)

    def test_signup_receive_activation_email(self):
        self.visit(self.url)
        self.create_user()

        # Wait for async sending of emails
        self.wait_celery_queue_to_be_empty(self._worker)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(tv.USER1_EMAIL, mail.outbox[0].to)
        self.assertIn("activate your account", mail.outbox[0].subject.lower())
        self.assertRegex(mail.outbox[0].body, "https?://.+/accounts/activate/.+/")

    def test_signup_activate_account(self):
        self.visit(self.url)
        self.create_user(activate_user=True)

        self.assertIn(
            "Your email has been verified, thank you! You may go ahead and log in now.",
            self.get_elem_text(self.main_panel),
        )

    def test_signup_activate_account_failed(self):
        self.visit(self.url)
        self.create_user()

        # User use a bad activation link
        bad_activation_link = "/accounts/activate/B4dT0k3n/"

        self.visit(bad_activation_link)
        self.assertIn(
            "could not activate the account", self.get_elem_text(self.main_panel)
        )


@override_settings(CELERY_BROKER_URL="memory://localhost")
@override_settings(CELERY_TASK_ROUTES={})
class SignupPageSetRegionSettingsTests(SignupPages, LoginPage, AccountPages):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.control.purge()
        cls._worker = app.Worker(app=app, pool="solo", concurrency=1)
        cls._thread = threading.Thread(target=cls._worker.start)
        cls._thread.daemon = True
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        cls._worker.stop()
        super().tearDownClass()

    def setUp(self, **kwargs):
        # first org and admin already created
        super().setUp(browser_locale="fr")
        self.admin_org = setup_org("admin org", "admin-org")
        setup_admin(org=self.admin_org)

    def test_browser_region_settings_detected_during_signup(self):
        # User create an account in the first org
        self.visit(SignupPages.url)
        browser_timezone = self.browser.execute_script(
            "return Intl.DateTimeFormat().resolvedOptions().timeZone"
        )

        self.create_user(activate_user=True)
        self.log_user()
        self.visit(AccountPages.update_region_settings_url)

        # Language is detected by django.middleware.locale.LocaleMiddleware
        self.assertEqual(self.get_elem_text(self.language_select), "Français")
        # Timezone is set by browser inside hidden input during signup
        self.assertEqual(self.get_elem_text(self.timezone_select), browser_timezone)
