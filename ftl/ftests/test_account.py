#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re
from unittest import skipIf
from unittest.mock import patch

from django.core import mail
from django_otp.middleware import OTPMiddleware
from selenium.common.exceptions import NoSuchElementException

from ftests.pages.account_pages import AccountPages
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_2fa_totp_device, \
    setup_2fa_static_device
from ftl.settings import DEV_MODE


def mocked_verify_user(self, request, user):
    user.is_verified = lambda: True
    user.otp_device = 'fake_device'
    return user


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
        self.assertEqual(10, len(self.get_elems_text(self.created_codes_list)))
        self.assertIn('print', self.get_elem_text(self.print_button).lower())

        # User go back to 2fa index page and can see the set he just added
        self.get_elem(self.cancel_button).click()
        self.assertIn(set_name, self.get_elem_text(self.emergency_codes_divs))

        # User logout
        self.visit(self.logout_url)

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
        self.visit(self.logout_url)

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
        self.visit(self.logout_url)

        # Remove middleware mock, to restore check pages
        self.middleware_patcher.stop()
        # Also remove totp device created during setup
        self.required_totp_device.delete()

        # When user login again there is no 2FA check page as there is no 2fa devices set
        self.log_user()
        self.assertIn('home', self.head_title)
