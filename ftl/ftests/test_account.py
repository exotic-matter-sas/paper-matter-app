#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re
from unittest import skipIf
from unittest.mock import patch, Mock

from django.core import mail
from django.http import HttpResponse
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from selenium.common.exceptions import NoSuchElementException

from ftests.pages.account_pages import AccountPages
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_2fa_totp_device, \
    setup_2fa_static_device, setup_2fa_fido2_device
from ftl.otp_plugins.otp_ftl import views_fido2
from ftl.settings import DEV_MODE


def mocked_verify_user(self, request, user):
    user.is_verified = lambda: True
    user.otp_device = 'fake_device'
    return user


def mocked_totp_time_setter(self, value):
    self._time = TotpDevice2FATests.secret_time


# These mocks need to be defined before Django (or test?) start
totp_time_setter = Mock(wraps=TOTP.time.fset)
totp_time_property = TOTP.time.setter(totp_time_setter)
mocked_fido2_api_register_begin = Mock(wraps=views_fido2.fido2_api_register_begin)
views_fido2.fido2_api_register_begin = mocked_fido2_api_register_begin


class BasicAccountPagesTests(LoginPage, AccountPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_change_email(self):
        # Go to account management / email change
        self.visit(AccountPages.update_email_url)

        # Enter form data
        self.update_email(tv.USER2_EMAIL)

        self.assertIn('A confirmation email has been sent', self.get_elem_text(self.success_notification))

        # Two emails should have been sent
        self.assertEqual(len(mail.outbox), 2)

        # Check notice email
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn('notice of email change', mail.outbox[0].subject.lower())
        self.assertIn('Someone requested to change the email address', mail.outbox[0].body)

        # Check validation email
        self.assertIn(tv.USER2_EMAIL, mail.outbox[1].to)
        self.assertIn('validate your new email', mail.outbox[1].subject.lower())
        self.assertRegex(mail.outbox[1].body, 'https?://.+/accounts/email/.+')

        # Check link
        validate_email_link = re.search(r'(https?://.+/accounts/email/.+)', mail.outbox[1].body)
        self.assertIsNotNone(validate_email_link)

        self.visit(validate_email_link.group(1), absolute_url=True)
        self.assertIn('Email successfully updated', self.get_elem_text(self.success_notification))

        # Logout
        self.visit(LoginPage.logout_url)

        # Ensure can't log with old email
        self.log_user()
        self.assertIn('email address and password', self.get_elem_text(self.login_failed_div),
                      'User login should failed using its old email')

        # User is able to login using its new email
        self.log_user(email=tv.USER2_EMAIL)
        self.assertIn('home', self.head_title,
                      'User login should success using its new email')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_change_password(self):
        # Go to account management / password change
        self.visit(AccountPages.update_password_url)

        # Enter form data
        new_password = "new password"
        self.update_password(tv.USER1_PASS, new_password)

        self.assertIn('Password updated!', self.get_elem_text("div.text-center"))

        # Logout
        self.visit(LoginPage.logout_url)

        # Ensure can't log with old password
        self.visit(LoginPage.url)
        self.log_user()
        self.assertIn('email address and password', self.get_elem_text(self.login_failed_div),
                      'User login should failed using its old password')

        # User is able to login using its new password
        self.log_user(password=new_password)
        self.assertIn('home', self.head_title,
                      'User login should success using its new password')


class StaticDevice2FATests(LoginPage, AccountPages):
    codes_list = ['AAA000', 'BBB111', 'CCC222', 'DDD333', 'EEE444', 'FFF555', 'GGG666', 'HHH777', 'III888',
                  'JJJ999']

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
        self.middleware_patcher = patch.object(OTPMiddleware, '_verify_user', mocked_verify_user)
        self.middleware_patcher.start()
        self.addCleanup(patch.stopall)  # ensure mock is remove after each test, even if the test crash

        self.visit(AccountPages.two_factors_authentication_url)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_add_emergency_code_set(self):
        # User add an emergency codes set
        set_name = 'My precious emergency code'
        self.add_emergency_codes_set(set_name)

        # User can see and print its codes from the confirmation page
        self.assertEqual(10, len(self.get_elems_text(self.emergency_codes_lists)))
        self.assertIn('print', self.get_elem_text(self.print_button).lower())

        # User go back to 2fa index page and can see the set he just added
        self.get_elem(self.cancel_button).click()
        self.assertIn(set_name, self.get_elem_text(self.emergency_codes_divs))

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for totp, emergency code could be use as an alternative
        self.assertIn('authenticator app', self.get_elem_text(self.check_pages_device_label).lower())
        self.assertIn('emergency code', self.get_elem_text(self.check_pages_alternatives_list))

        # User click and emergency code alternative and corresponding check page is displayed
        self.get_elem(self.check_pages_alternatives_list).click()
        self.assertIn('emergency codes', self.get_elem_text(self.check_pages_device_label).lower())

    def test_use_emergency_code(self):
        # User already added an emergency code set and used 9 of the 10 codes of the set
        # User is logged out
        code_left = self.codes_list[0]
        first_set_name = 'First set'
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
        self.assertIn('invalid', self.get_elem_text(self.emergency_codes_divs).lower())
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.emergency_codes_lists)

        # User logout
        self.visit(self.logout_url)

        # On next login and 2FA check, emergency code could no more be used as the only available set is empty
        # TODO dont display empty code set as an alternative ?
        self.log_user()
        self.get_elem(self.check_pages_alternatives_list).click()
        self.assertIn('error', self.get_elem_text('body').lower())

        # User cancel check
        self.get_elem(self.cancel_button).click()

        # If totp device is removed and user log again there is no check made as it only remain an empty emergency codes
        # set
        self.required_totp_device.delete()
        # TODO currently a check is made and user is stuck out of its account because he can't give a code of an empty
        #  set
        # self.log_user()
        # self.assertIn('home', self.head_title)
        #
        # # User cancel check
        # self.get_elem(self.cancel_button).click()

        # If another set is added only the new set appears in the codes set select
        second_set_name = 'Second set'
        setup_2fa_static_device(self.user, second_set_name, self.codes_list)

        self.log_user()
        self.assertNotIn(first_set_name, self.get_elems_text(self.check_pages_device_select_options))
        self.assertIn(second_set_name, self.get_elems_text(self.check_pages_device_select_options))

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

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_rename_emergency_code_set(self):
        # User already added an emergency code set
        old_set_name = 'Old set name'
        setup_2fa_static_device(self.user, old_set_name, self.codes_list)
        self.visit(self.two_factors_authentication_url)  # refresh page

        # User rename existing emergency code
        new_set_name = 'New set name'
        self.rename_emergency_codes_set(new_name=new_set_name)

        # User see the set name have been updated in the device list
        self.assertNotIn(old_set_name, self.get_elem_text(self.emergency_codes_divs))
        self.assertIn(new_set_name, self.get_elem_text(self.emergency_codes_divs))

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for totp, user click on emergency code alternative
        self.get_elem(self.check_pages_alternatives_list).click()

        # The new code set name is available in the select
        self.assertEqual(new_set_name, self.get_elem_text(self.check_pages_device_input))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_delete_emergency_code_set(self):
        # User already added an emergency code set
        setup_2fa_static_device(self.user, codes_list=self.codes_list)
        self.visit(self.two_factors_authentication_url)  # refresh page

        # User delete existing emergency code
        self.delete_emergency_codes_set()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.emergency_codes_divs)

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()
        # Also remove totp device created during setup
        self.required_totp_device.delete()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn('home', self.head_title)


class TotpDevice2FATests(LoginPage, AccountPages):
    secret_time = 1582109713.4242425
    secret_key = 'f679758a45fa55cd14b583c8505bf4d12eb76f27'
    valid_token = '954370'  # value get from TOTP.token() in debug mode with the 2 settings above

    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged to 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(OTPMiddleware, '_verify_user', mocked_verify_user)
        self.middleware_patcher.start()
        self.addCleanup(patch.stopall)  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

        self.visit(LoginPage.url)
        self.log_user()
        self.visit(AccountPages.two_factors_authentication_url)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_add_auth_app_unconfirmed(self):
        # User add an auth app
        device_name = 'My precious yPhone xD'
        self.add_auth_app(device_name)

        # User can see qr code to scan
        self.get_elem(self.qr_code_image)

        # User have lost its smartphone under its pillow, he click on the cancel button
        self.get_elem(self.cancel_button).click()

        # Totp device appears in the list as not confirmed
        self.assertIn('not confirmed', self.get_elem_text(self.auth_app_divs).lower())

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User log again
        self.log_user()

        # There is no 2FA check as totp device setup isn't complete
        self.assertIn('home', self.head_title)

    @patch.object(TOTP, 'time', totp_time_property)
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_add_auth_app_confirmed(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # User has already add an unconfirmed auth app
        device_name = 'My precious yPhone xD'
        setup_2fa_totp_device(self.user, device_name, secret_key=self.secret_key, confirmed=False)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User resume its totp device setup
        self.get_elem(self.unconfirmed_badges).click()

        # User can see qr code to scan
        self.get_elem(self.qr_code_image)

        # User scan the QR code and input generated code
        self.get_elem(self.totp_code_setup_input).send_keys(self.valid_token)
        self.get_elem(self.confirm_button).click()

        # User is invited to add a emergency code as backup
        self.assertIn('emergency codes', self.get_elem_text(self.device_name_label).lower())

        # User go back to 2fa index page and can see the auth app he just added
        self.get_elem(self.cancel_button).click()
        self.assertIn(device_name, self.get_elem_text(self.auth_app_divs))
        self.assertNotIn('not confirmed', self.get_elem_text(self.auth_app_divs).lower(),
                         'The totp device should be confirmed')

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for totp
        self.assertIn('authenticator app', self.get_elem_text(self.check_pages_device_label).lower())

        # No alternative 2FA are shown
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.check_pages_alternatives_list)

        # User can complete login using a valid 2FA code
        self.enter_2fa_code(self.valid_token)
        self.assertIn('home', self.head_title)

    @patch.object(TOTP, 'time', totp_time_property)
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_add_auth_app_with_emergency_code_already_set(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter
        setup_2fa_static_device(self.user) # emergency code already set

        # User has already add an unconfirmed auth app
        device_name = 'My precious yPhone xD'
        setup_2fa_totp_device(self.user, device_name, secret_key=self.secret_key, confirmed=False)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User resume its totp device setup
        self.get_elem(self.unconfirmed_badges).click()

        # User can see qr code to scan
        self.get_elem(self.qr_code_image)

        # User scan the QR code and input generated code
        self.get_elem(self.totp_code_setup_input).send_keys(self.valid_token)
        self.get_elem(self.confirm_button).click()

        # User has already a "emergency codes set" set, so he get redirected to 2FA devices list
        self.wait_for_elem_to_show(self.auth_app_divs)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_rename_auth_app(self):
        # User has already add an unconfirmed auth app
        old_device_name = 'Nokia 3310'
        setup_2fa_totp_device(self.user, old_device_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User rename existing emergency code
        new_device_name = 'My precious yPhone xD'
        self.rename_auth_app(new_name=new_device_name)

        # User see the set name have been updated in the device list
        self.assertNotIn(old_device_name, self.get_elem_text(self.auth_app_divs))
        self.assertIn(new_device_name, self.get_elem_text(self.auth_app_divs))

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # The new device name is available in the select
        self.assertEqual(new_device_name, self.get_elem_text(self.check_pages_device_input))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_delete_auth_app(self):
        # User has already add an unconfirmed auth app
        setup_2fa_totp_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing emergency code
        self.delete_auth_app()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.auth_app_divs)

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn('home', self.head_title)


class Fido2Device2FATests(LoginPage, AccountPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged to 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(OTPMiddleware, '_verify_user', mocked_verify_user)
        self.middleware_patcher.start()
        self.addCleanup(patch.stopall)  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(mocked_fido2_api_register_begin.reset_mock, return_value=True)

        self.visit(LoginPage.url)
        self.log_user()
        self.visit(AccountPages.two_factors_authentication_url)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_add_security_key_fail_and_trigger_error(self):
        # make fido2 api return a fake value for js code to fail quickly during device registration
        mocked_fido2_api_register_begin.return_value = HttpResponse('error')

        # User add a security key
        key_name = 'O Key'
        self.add_security_key(key_name)

        # User should be prompted by browser to enter its key (can't be really tested)
        self.assertEqual(1, mocked_fido2_api_register_begin.call_count)
        self.assertIn('cbor-decode', self.get_elem_text(self.error_message))

        # User have to go back to the list as an error occurred
        self.get_elem(self.cancel_button).click()

        # No device have been added to the list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.security_key_divs)

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User log again
        self.log_user()

        # There is no 2FA check as fido2 device setup have fail
        self.assertIn('home', self.head_title)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_security_key_added(self):
        # User has already added a security key
        key_name = 'O Key'
        setup_2fa_fido2_device(self.user, name=key_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User can see the security key in the list
        self.assertIn(key_name, self.get_elem_text(self.security_key_divs))

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # User login again, the 2fa check page appears.
        self.log_user()

        # Check page appears ask for fido2
        self.assertIn('security key', self.get_elem_text(self.confirm_button).lower())

        # No alternative 2FA are shown
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.check_pages_alternatives_list)

        # User can complete login using a valid security key (can't be tested)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_rename_security_key(self):
        # User has already added a security key
        old_key_name = 'MO Key'
        setup_2fa_fido2_device(self.user, name=old_key_name)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User rename existing security key
        new_key_name = 'O Key'
        self.rename_security_key(new_name=new_key_name)

        # User see the key name have been updated in the device list
        self.assertNotIn(old_key_name, self.get_elem_text(self.security_key_divs))
        self.assertIn(new_key_name, self.get_elem_text(self.security_key_divs))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_delete_security_key(self):
        # User has already added a security key
        setup_2fa_fido2_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User delete existing emergency code
        self.delete_security_key()

        # User see the set have been remove from the device list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.security_key_divs)

        # User logout
        self.get_elem(self.logout_button).click()

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn('home', self.head_title)
