#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re
from unittest import skipIf

from django.core import mail

from ftests.pages.account_pages import AccountPages
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import DEV_MODE


class AccountPageTests(LoginPage, AccountPages):
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
