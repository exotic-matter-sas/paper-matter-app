#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

import re
import threading
from unittest.mock import patch, Mock

from django.core import mail
from django.http import HttpResponse
from django.test import override_settings
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from selenium.common.exceptions import NoSuchElementException

from core.tasks import batch_delete_doc, batch_delete_org
from ftests.pages.account_pages import AccountPages
from ftests.pages.home_page import HomePage
from ftests.pages.login_page import LoginPage
from ftests.pages.signup_pages import SignupPages
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_2fa_totp_device,
    setup_2fa_static_device,
    setup_2fa_fido2_device,
    setup_document,
)
from ftests.tools.test_values import (
    TOTP_DEVICE_SECRET_TIME,
    TOTP_DEVICE_SECRET_KEY,
    TOTP_DEVICE_VALID_TOKEN,
    TOTP_DEVICE_INVALID_TOKEN,
)
from ftl.celery import app
from ftl.otp_plugins.otp_ftl import views_fido2


def mocked_verify_user(self, request, user):
    user.is_verified = lambda: True
    user.otp_device = "fake_device"
    return user


def mocked_totp_time_setter(self, value):
    self._time = TOTP_DEVICE_SECRET_TIME


# These mocks need to be defined before Django (or test?) start
totp_time_setter = Mock(wraps=TOTP.time.fset)
totp_time_property = TOTP.time.setter(totp_time_setter)
mocked_fido2_api_register_begin = Mock(wraps=views_fido2.fido2_api_register_begin)
views_fido2.fido2_api_register_begin = mocked_fido2_api_register_begin


@override_settings(CELERY_BROKER_URL="memory://localhost")
@override_settings(CELERY_TASK_ROUTES={})
class BasicAccountPagesTests(LoginPage, AccountPages):
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
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.visit(LoginPage.url)
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

    def test_change_email(self):
        # Go to account management / email change
        self.visit(AccountPages.update_email_url)

        # Enter form data
        self.update_email(tv.USER2_EMAIL)

        self.assertIn(
            "A confirmation email has been sent",
            self.get_elem_text(self.success_notification),
        )

        # Wait for async sending of emails
        self.wait_celery_queue_to_be_empty(self._worker)

        # Two emails should have been sent
        self.assertEqual(len(mail.outbox), 2)

        # Check notice email
        self.assertIn(tv.ADMIN1_EMAIL, mail.outbox[0].to)
        self.assertIn("notice of email change", mail.outbox[0].subject.lower())
        self.assertIn(
            "Someone requested to change the email address", mail.outbox[0].body
        )

        # Check validation email
        self.assertIn(tv.USER2_EMAIL, mail.outbox[1].to)
        self.assertIn("validate your new email", mail.outbox[1].subject.lower())
        self.assertRegex(mail.outbox[1].body, "https?://.+/accounts/email/.+")

        # Check link
        validate_email_link = re.search(
            r"(https?://.+/accounts/email/.+)", mail.outbox[1].body
        )
        self.assertIsNotNone(validate_email_link)

        self.visit(validate_email_link.group(1), absolute_url=True)
        self.assertIn(
            "Email successfully updated", self.get_elem_text(self.success_notification)
        )

        # Logout
        self.visit(LoginPage.logout_url)

        # Ensure can't log with old email
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)
        self.assertIn(
            "email address and password",
            self.get_elem_text(self.login_failed_div),
            "User login should failed using its old email",
        )

        # User is able to login using its new email
        self.log_user(email=tv.USER2_EMAIL, password=tv.ADMIN1_PASS)
        self.assertIn(
            "home", self.head_title, "User login should success using its new email"
        )

    def test_change_password(self):
        # Go to account management / password change
        self.visit(AccountPages.update_password_url)

        # Enter form data
        new_password = "new password"
        self.update_password(tv.ADMIN1_PASS, new_password)

        self.assertIn("Password updated!", self.get_elem_text("div.text-center"))

        # Wait for async sending of emails
        self.wait_celery_queue_to_be_empty(self._worker)

        # Check notice email
        self.assertIn(tv.ADMIN1_EMAIL, mail.outbox[0].to)
        self.assertIn("notice of password change", mail.outbox[0].subject.lower())
        self.assertIn(
            "The password of your Paper Matter account has been updated",
            mail.outbox[0].body,
        )

        # Logout
        self.visit(LoginPage.logout_url)

        # Ensure can't log with old password
        self.visit(LoginPage.url)
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)
        self.assertIn(
            "email address and password",
            self.get_elem_text(self.login_failed_div),
            "User login should failed using its old password",
        )

        # User is able to login using its new password
        self.log_user(email=tv.ADMIN1_EMAIL, password=new_password)
        self.assertIn(
            "home", self.head_title, "User login should success using its new password"
        )


class RegionAccountPageTests(LoginPage, HomePage, AccountPages, SignupPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp(browser_locale="fr")  # browser local is french
        self.admin_org = setup_org(name="admin org 1", slug="admin-org-1")
        setup_admin(self.admin_org)
        self.user_org = setup_org()

    def test_user_is_missing_region_settings(self):
        # Given user is missing lang and tz
        setup_user(self.user_org, lang="", tz="")
        self.visit(LoginPage.url)
        self.log_user()

        # When he go to update region page
        self.visit(AccountPages.update_region_settings_url)

        # Selects have no value set (--)
        self.assertEqual(self.get_elem_text(self.language_select), "--")
        self.assertEqual(self.get_elem_text(self.timezone_select), "--")

        # Default locale come from browser (french for this test)
        self.assertIn("compte", self.head_title)
        # Default timezone come from TIME_ZONE settings (UTC currently)
        self.assertEqual("UTC", self.get_elem_attribute("#current-time", "title"))

    def test_user_have_region_settings(self):
        # Given user get custom region settings
        user_timezone_setting = "Europe/Amsterdam"
        setup_user(self.user_org, lang="en", tz=user_timezone_setting)
        self.visit(LoginPage.url)
        self.log_user()

        # When he go to update region page
        self.visit(AccountPages.update_region_settings_url)

        # Selects have proper values sets
        self.assertEqual(self.get_elem_text(self.language_select), "English")
        self.assertEqual(
            self.get_elem_text(self.timezone_select), user_timezone_setting
        )

        # Locale come from user setting
        self.assertIn("account", self.head_title)
        # Timezone come from user setting
        self.assertEqual("CET", self.get_elem_attribute("#current-time", "title"))

    def test_user_update_region_language(self):
        setup_user(self.user_org)
        self.visit(LoginPage.url)
        # language on non logged page is Fr (due to browser setting)
        self.assertIn("connecter", self.head_title)

        self.log_user()

        # language on logged page is En (due to user setting)
        self.assertIn("home", self.head_title)  # Django string
        self.assertIn(
            "Search",
            self.get_elem_text(self.search_button),
            "Vue string should be translated according to user settings",
        )  # Vue string

        # User go to update region page
        self.visit(AccountPages.update_region_settings_url)

        # He update its language to Fr
        self.update_region_settings(language="Français")

        # Language on logged page is now Fr (due to user setting)
        self.visit(HomePage.url)
        self.assertIn("accueil", self.head_title)  # Django string
        self.assertIn(
            "Rechercher", self.get_elem_text(self.search_button)
        )  # Vue string

    def test_user_update_region_timezone(self):
        # user has already added a document and log in
        user = setup_user(self.user_org, tz="America/New_York")
        setup_document(self.user_org, user)
        self.visit(LoginPage.url)
        self.log_user()

        # We store the current document add time
        self.wait_documents_list_loaded()
        initial_document_add_time = re.search(
            r"(\d{1,2}):(\d{1,2})",
            self.get_elem_attribute(self.first_document_date, "title"),
        )
        initial_document_add_hours = int(initial_document_add_time.group(1))

        initial_document_add_minutes = int(initial_document_add_time.group(2))

        # User go to update region page
        self.visit(AccountPages.update_region_settings_url)

        # He update its timezone to Chicago
        self.update_region_settings(timezone="America/Chicago")

        # User go back to home page
        self.visit(HomePage.url)
        self.wait_documents_list_loaded()

        # Document date have been updated
        updated_document_add_time = re.search(
            r"(\d{1,2}):(\d{1,2})",
            self.get_elem_attribute(self.first_document_date, "title"),
        )
        updated_document_add_hours = int(updated_document_add_time.group(1))
        updated_document_add_minutes = int(updated_document_add_time.group(2))

        # Chicago hour = New York hour - 1 (hours are displayed in a.m./p.m. format)
        self.assertEqual(
            updated_document_add_hours,
            12 if initial_document_add_hours == 1 else initial_document_add_hours - 1,
        )
        self.assertEqual(updated_document_add_minutes, initial_document_add_minutes)


class DeleteAccountPageTests(LoginPage, AccountPages, SignupPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.admin_org = setup_org(name="admin org 1", slug="admin-org-1")
        setup_admin(self.admin_org)
        self.user_org = setup_org()
        self.user = setup_user(self.user_org)

        self.visit(LoginPage.url)

    def test_user_can_delete_its_account(self):
        # normal user is logged
        self.log_user()

        # User go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # User submit password to confirm account deletion
        self.delete_account(tv.USER1_PASS)

        # User has been redirected to login page with a message confirming the deletion
        self.assertIn(
            "account was deleted", self.get_elem_text(self.success_notification)
        )

        # User is no more able to login to its deleted account
        self.log_user()
        self.assertIn(
            "email address and password",
            self.get_elem_text(self.login_failed_div),
            "User login should failed as its account should be deleted",
        )

    def test_unique_admin_cant_delete_its_account(self):
        # admin user is logged
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

        # User go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # Can't delete the last administrator
        self.assertIn(
            "holds the last administrator", self.get_elem_text(self.error_message),
        )
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.submit_account_deletion)

    def test_non_unique_admin_can_delete_its_account(self):
        # Create a second admin in a second org
        admin_org2 = setup_org("admin org 2", "admin-org-2")
        setup_admin(admin_org2, tv.ADMIN2_EMAIL, tv.ADMIN2_PASS)
        # admin1 user is logged
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

        # Admin go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # Admin submit password to confirm account deletion
        self.delete_account(tv.ADMIN1_PASS)

        # Admin has been redirected to login page with a message confirming the deletion
        self.assertIn(
            "account was deleted", self.get_elem_text(self.success_notification)
        )

        # Admin is no more able to login as a user to its deleted account
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)
        self.assertIn(
            "email address and password",
            self.get_elem_text(self.login_failed_div),
            "Admin login should failed as its account should be deleted",
        )

    @override_settings(FTL_DELETE_DISABLED_ACCOUNTS=False)
    def test_disabled_account_cant_be_reused_with_signup(self):
        # normal user is logged
        self.log_user()

        # User go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # User submit password to confirm account deletion
        self.delete_account(tv.USER1_PASS)

        # Faking the hourly batch-delete-documents CRON call
        batch_delete_doc()
        # Faking the daily CRON batch-delete-orgs
        batch_delete_org()

        # User try to recreate its account using the same email and org name
        self.visit(SignupPages.url)
        self.create_user()

        # Org field and email field display an error
        self.assertIn(
            "organization can't be used.",
            self.get_elem_text(self.org_error_message).lower(),
        )
        self.assertIn(
            "email can't be used", self.get_elem_text(self.email_error_message).lower()
        )

    @override_settings(FTL_DELETE_DISABLED_ACCOUNTS=False)
    def test_disabled_user_email_cant_be_reused_with_email_update(self):
        # normal user is logged
        self.log_user()

        # User go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # User submit password to confirm account deletion
        self.delete_account(tv.USER1_PASS)

        # Faking the hourly batch-delete-documents CRON call
        batch_delete_doc()
        # Faking the daily CRON batch-delete-orgs
        batch_delete_org()

        # Admin user login
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

        # Admin go to account management / email change
        self.visit(AccountPages.update_email_url)

        # And try to update its email using the same used by the disabled user
        self.update_email(tv.USER1_PASS)

        # Org field and email field display an error
        self.assertIn(
            "enter a valid email address",
            self.get_elem_text(self.error_message).lower(),
        )

    @override_settings(FTL_DELETE_DISABLED_ACCOUNTS=True)
    def test_deleted_account_can_be_reused(self):
        # normal user is logged
        self.log_user()

        # User go to account management / password change
        self.visit(AccountPages.delete_account_url)

        # User submit password to confirm account deletion
        self.delete_account(tv.USER1_PASS)

        # Faking the hourly batch-delete-documents CRON call
        batch_delete_doc()
        # Faking the daily CRON batch-delete-orgs
        batch_delete_org()

        # User try to recreate its account using the same email and org name
        self.visit(SignupPages.url)
        self.create_user()

        # Account has been created
        self.assertIn(
            "verify your email inbox to activate your account",
            self.get_elem(self.main_panel).text,
        )


class StaticDevice2FATests(LoginPage, AccountPages):
    codes_list = [
        "AAA000",
        "BBB111",
        "CCC222",
        "DDD333",
        "EEE444",
        "FFF555",
        "GGG666",
        "HHH777",
        "III888",
        "JJJ999",
    ]

    def setUp(self, **kwargs):
        # first org, admin, user, first 2fa device are already created, user is already logged on 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()
        # setup the first device to access emergency codes feature
        self.required_totp_device = setup_2fa_totp_device(self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash

        self.visit(AccountPages.two_factors_authentication_url)

    def test_add_emergency_code_set(self):
        # User add an emergency codes set
        set_name = "My precious emergency code"
        self.add_emergency_codes_set(set_name)

        # User can see and print its codes from the confirmation page
        self.assertEqual(10, len(self.get_elems_text(self.emergency_codes_lists)))
        self.assertIn("print", self.get_elem_text(self.print_button).lower())

        # User go back to 2fa index page and can see the set he just added
        self.get_elem(self.cancel_button).click()
        self.assertIn(set_name, self.get_elem_text(self.emergency_codes_divs))

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for totp, emergency code could be use as an alternative
        self.assertIn(
            "authenticator app",
            self.get_elem_text(self.check_pages_device_label).lower(),
        )
        self.assertIn(
            "emergency code", self.get_elem_text(self.check_pages_alternatives_list)
        )

        # User click and emergency code alternative and corresponding check page is displayed
        self.get_elem(self.check_pages_alternatives_list).click()
        self.assertIn(
            "emergency codes", self.get_elem_text(self.check_pages_device_label).lower()
        )

    def test_use_emergency_code(self):
        # User already added an emergency code set and used 9 of the 10 codes of the set
        # User is logged out
        code_left = self.codes_list[0]
        first_set_name = "First set"
        setup_2fa_static_device(self.user, first_set_name, [code_left])
        self.visit(self.logout_url)
        self.middleware_patcher.stop()  # Remove middleware mock, to restore check pages

        # User login to its account using the last emergency code
        self.log_user()
        self.get_elem(self.check_pages_alternatives_list).click()
        self.enter_2fa_code(code_left)

        # User see red badges next to its email, inside dropdown menu, and next to 2FA menu
        # He click on them to know what's wrong
        self.get_elem(self.no_code_left_badges).click()
        self.get_elems(self.no_code_left_badges)[1].click()
        self.get_elem(self.no_code_left_badges).click()

        # He can see that all the codes of the set have been used, too bad
        self.assertIn("invalid", self.get_elem_text(self.emergency_codes_divs).lower())
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.emergency_codes_lists)

        # User logout
        self.visit(self.logout_url)

        # On next login and 2FA check, emergency code are no more available as the only available set is empty
        self.log_user()
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.check_pages_alternatives_list)

        # User cancel check
        self.get_elem(self.cancel_button).click()

        # If another set is added only the new set appears in the codes set select
        second_set_name = "Second set"
        setup_2fa_static_device(self.user, second_set_name, self.codes_list)

        self.log_user()
        self.get_elem(self.check_pages_alternatives_list).click()
        self.assertNotIn(
            first_set_name, self.get_elems_text(self.check_pages_device_select_options)
        )
        self.assertIn(
            second_set_name, self.get_elems_text(self.check_pages_device_select_options)
        )

        # User complete login using a code of the new set and finally remove the old empty code set (at least!)
        used_code = self.codes_list[3]
        self.enter_2fa_code(used_code)

        self.visit(self.two_factors_authentication_url)
        self.delete_emergency_codes_set()

        # The red badges are no more displayed on account page or home page
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.no_code_left_badges)

        self.visit(HomePage.url)
        self.get_elem(HomePage.profile_name).click()

        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.no_code_left_badges)

    def test_rename_emergency_code_set(self):
        # User already added an emergency code set
        old_set_name = "Old set name"
        setup_2fa_static_device(self.user, old_set_name, self.codes_list)
        self.visit(self.two_factors_authentication_url)  # refresh page

        # User rename existing emergency code
        new_set_name = "New set name"
        self.rename_emergency_codes_set(new_name=new_set_name)

        # User see the set name have been updated in the device list
        self.assertNotIn(old_set_name, self.get_elem_text(self.emergency_codes_divs))
        self.assertIn(new_set_name, self.get_elem_text(self.emergency_codes_divs))

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()
        self.wait_for_elem_to_disappear(self.login_submit_input)

        # Check page appears ask for totp, user click on emergency code alternative
        self.get_elem(self.check_pages_alternatives_list).click()

        # The new code set name is available in the select
        self.assertEqual(
            new_set_name, self.get_elem_text(self.check_pages_device_input)
        )

    def test_delete_emergency_code_set(self):
        # User already added an emergency code set
        setup_2fa_static_device(self.user, codes_list=self.codes_list)
        self.visit(self.two_factors_authentication_url)  # refresh page

        # User delete existing emergency code
        self.get_elems(self.delete_emergency_codes_buttons)[0].click()

        # There is no special warning about it, as there there is auth app 2fa left
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.delete_warning)
        self.get_elem(self.confirm_button).click()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.emergency_codes_divs)

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()
        # Also remove totp device created during setup
        self.required_totp_device.delete()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn("home", self.head_title)


class TotpDevice2FATests(LoginPage, AccountPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged to 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

        self.visit(LoginPage.url)
        self.log_user()
        self.visit(AccountPages.two_factors_authentication_url)

    def test_add_auth_app_unconfirmed(self):
        # User add an auth app
        device_name = "My precious yPhone xD"
        self.add_auth_app(device_name)

        # User can see qr code to scan
        self.get_elem(self.qr_code_image)

        # User have lost its smartphone under its pillow, he click on the cancel button
        self.get_elem(self.cancel_button).click()

        # Totp device appears in the list as not confirmed
        self.assertIn("not confirmed", self.get_elem_text(self.auth_app_divs).lower())

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User log again
        self.log_user()

        # There is no 2FA check as totp device setup isn't complete
        self.assertIn("home", self.head_title)

    @patch.object(TOTP, "time", totp_time_property)
    def test_add_auth_app_confirmed(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # User has already add an unconfirmed auth app
        device_name = "My precious yPhone xD"
        setup_2fa_totp_device(
            self.user, device_name, secret_key=TOTP_DEVICE_SECRET_KEY, confirmed=False
        )
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User resume its totp device setup
        self.get_elem(self.unconfirmed_badges).click()

        # User can see qr code to scan
        self.get_elem(self.qr_code_image)

        # User scan the QR code and input generated code
        self.enter_2fa_code(TOTP_DEVICE_VALID_TOKEN)

        # User is invited to add a emergency code as backup
        self.assertIn(
            "emergency codes", self.get_elem_text(self.device_name_label).lower()
        )

        # User go back to 2fa index page and can see the auth app he just added
        self.get_elem(self.cancel_button).click()
        self.assertIn(device_name, self.get_elem_text(self.auth_app_divs))
        self.assertNotIn(
            "not confirmed",
            self.get_elem_text(self.auth_app_divs).lower(),
            "The totp device should be confirmed",
        )

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for totp
        self.assertIn(
            "authenticator app",
            self.get_elem_text(self.check_pages_device_label).lower(),
        )

        # No alternative 2FA are shown
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.check_pages_alternatives_list)

        # User can complete login using a valid 2FA code
        self.enter_2fa_code(TOTP_DEVICE_VALID_TOKEN)
        self.assertIn("home", self.head_title)

    @patch.object(TOTP, "time", totp_time_property)
    def test_add_auth_app_with_wrong_confirmation_code(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter
        setup_2fa_static_device(self.user)  # emergency code already set

        # User has already add an unconfirmed auth app and resume its totp device setup
        device_name = "My precious yPhone xD"
        setup_2fa_totp_device(
            self.user, device_name, secret_key=TOTP_DEVICE_SECRET_KEY, confirmed=False
        )
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page
        self.get_elem(self.unconfirmed_badges).click()

        # User enter invalid code
        self.enter_2fa_code(TOTP_DEVICE_INVALID_TOKEN)

        # An error message appears
        self.get_elem(self.error_message)

    @patch.object(TOTP, "time", totp_time_property)
    def test_add_auth_app_with_emergency_code_already_set(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter
        setup_2fa_static_device(self.user)  # emergency code already set

        # User has already add an unconfirmed auth app and resume its totp device setup
        device_name = "My precious yPhone xD"
        setup_2fa_totp_device(
            self.user, device_name, secret_key=TOTP_DEVICE_SECRET_KEY, confirmed=False
        )
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page
        self.get_elem(self.unconfirmed_badges).click()

        # User scan the QR code and input generated code
        self.enter_2fa_code(TOTP_DEVICE_VALID_TOKEN)

        # User has already a "emergency codes set" set, so he get redirected to 2FA devices list
        self.wait_for_elem_to_show(self.auth_app_divs)

    def test_rename_auth_app(self):
        # User has already add an unconfirmed auth app
        old_device_name = "Nokia 3310"
        setup_2fa_totp_device(self.user, old_device_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User rename existing emergency code
        new_device_name = "My precious yPhone xD"
        self.rename_auth_app(new_name=new_device_name)

        # User see the set name have been updated in the device list
        self.assertNotIn(old_device_name, self.get_elem_text(self.auth_app_divs))
        self.assertIn(new_device_name, self.get_elem_text(self.auth_app_divs))

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()
        self.wait_for_elem_to_disappear(self.login_submit_input)

        # The new device name is available in the select
        self.assertEqual(
            new_device_name, self.get_elem_text(self.check_pages_device_input)
        )

    def test_delete_auth_app(self):
        # User has already added an auth app
        setup_2fa_totp_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing auth app
        self.delete_auth_app()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.auth_app_divs)

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn("home", self.head_title)

    def test_delete_auth_app_with_emergency_code(self):
        # User has already added an auth app and a emergency codes set
        setup_2fa_totp_device(self.user)
        setup_2fa_static_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing auth app
        self.get_elems(self.delete_auth_app_buttons)[0].click()

        # A warning message appears to inform user 2FA will be completely disable as emergency code are only available
        # when another 2fa device type is set
        self.assertIn("last 2FA device", self.get_elem_text(self.delete_warning))


class Fido2Device2FATests(LoginPage, AccountPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged to 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(mocked_fido2_api_register_begin.reset_mock, return_value=True)

        self.visit(LoginPage.url)
        self.log_user()
        self.visit(AccountPages.two_factors_authentication_url)

    def test_add_security_key_fail_and_trigger_error(self):
        # make fido2 api return a fake value for js code to fail quickly during device registration
        mocked_fido2_api_register_begin.return_value = HttpResponse("error")

        # User add a security key
        key_name = "O Key"
        self.add_security_key(key_name)

        # User should be prompted by browser to enter its key (can't be really tested)
        self.wait_for_elem_to_show(self.error_message)
        self.assertEqual(1, mocked_fido2_api_register_begin.call_count)
        self.assertIn("cbor-decode", self.get_elem_text(self.error_message))

        # User have to go back to the list as an error occurred
        self.get_elem(self.cancel_button).click()

        # No device have been added to the list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.security_key_divs)

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User log again
        self.log_user()
        self.wait_for_elem_to_disappear(self.login_submit_input)

        # There is no 2FA check as fido2 device setup have fail
        self.assertIn("home", self.head_title)

    def test_security_key_added(self):
        # User has already added a security key
        key_name = "O Key"
        setup_2fa_fido2_device(self.user, name=key_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User can see the security key in the list
        self.assertIn(key_name, self.get_elem_text(self.security_key_divs))

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for fido2
        self.assertIn("security key", self.get_elem_text(self.confirm_button).lower())

        # No alternative 2FA are shown
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.check_pages_alternatives_list)

        # User can complete login using a valid security key (can't be tested)

    def test_rename_security_key(self):
        # User has already added a security key
        old_key_name = "MO Key"
        setup_2fa_fido2_device(self.user, name=old_key_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User rename existing security key
        new_key_name = "O Key"
        self.rename_security_key(new_name=new_key_name)

        # User see the key name have been updated in the device list
        self.wait_for_elem_to_show(self.security_key_divs)
        self.assertNotIn(old_key_name, self.get_elem_text(self.security_key_divs))
        self.assertIn(new_key_name, self.get_elem_text(self.security_key_divs))

    def test_delete_security_key(self):
        # User has already added a security key
        setup_2fa_fido2_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing security key
        self.delete_security_key()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.security_key_divs)

        # User logout
        self.visit(LoginPage.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn("home", self.head_title)

    def test_delete_security_key_with_emergency_code(self):
        # User has already added a security key and a emergency codes set
        setup_2fa_fido2_device(self.user)
        setup_2fa_static_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing security key
        self.get_elems(self.delete_security_key_buttons)[0].click()

        # A warning message appears to inform user 2FA will be completely disable as emergency code are only available
        # when another 2fa device type is set
        self.assertIn("last 2FA device", self.get_elem_text(self.delete_warning))
