#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

import re

from django.core import mail
from django.test import override_settings

from ftests.pages.home_page import HomePage
from ftests.pages.login_page import LoginPage
from ftests.pages.reset_password_pages import ResetPasswordPages
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class LoginPageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created
        super().setUp()
        org = setup_org()
        self.admin = setup_admin(org=org)
        # User have already created its account
        self.user = setup_user(org=org)

    def test_fdgdfgd(self):
        # User login and is redirected to the home page
        self.visit(LoginPage.url)
        self.visit(LoginPage.url)

    def test_first_user_can_login(self):
        # User login and is redirected to the home page
        self.visit(LoginPage.url)
        self.log_user()

        # He can see its email on it
        self.assertIn("home", self.head_title)
        self.assertIn(self.user.email, self.get_elem(self.profile_name).text)

    def test_login_failed(self):
        # User login and is redirect to the logged home page
        self.visit(LoginPage.url)
        self.log_user(user_num=2)  # User2 doesn't exist

        # User stay on login page and an error message is displayed
        self.assertIn("login", self.head_title)
        self.assertIn(
            "Please enter a correct email address and password",
            self.get_elem(self.login_failed_div).text,
        )

    def test_login_page_redirect_logged_user(self):
        # User login
        self.visit(LoginPage.url)
        self.log_user()

        # User access login page again
        self.visit(LoginPage.url)

        # User is redirected to home page as he is already logged
        self.assertIn("Home", self.browser.title)

    @override_settings(AXES_ENABLED=True)
    def test_account_locked(self):
        self.visit(LoginPage.url)

        self.log_user(password="wrongpassword")
        self.log_user(password="wrongpassword")
        self.log_user(password="wrongpassword")
        self.log_user(password="wrongpassword")
        self.log_user(password="wrongpassword")

        self.assertIn("account locked", self.head_title)

        self.visit(LoginPage.url)
        self.log_user()
        self.assertIn("account locked", self.head_title)


class ForgotPasswordTests(LoginPage, ResetPasswordPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created
        super().setUp()
        org = setup_org()
        setup_admin(org=org)
        # User have already created its account
        self.user = setup_user(org=org)

    def test_password_forgot_send_email(self):
        # User want to login
        self.visit(LoginPage.url)

        # But as he forgot its password he click on the related link
        self.get_elem(self.password_reset_link).click()
        self.assertIn("Reset password", self.browser.title)

        # User fulfil the password reset form
        self.reset_password_step1(self.user.email)
        self.assertIn(
            "instructions for setting your password",
            self.get_elem_text(self.login_messages),
            "A confirmation message should tell user to check its emails",
        )

        # User received the email with the link to reset its password
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn("set new password", mail.outbox[0].subject.lower())
        self.assertRegex(mail.outbox[0].body, "https?://.+/reset/.+/.+/")

    def test_password_reset_link_working_properly(self):
        # User already received the reset password email
        self.visit(ResetPasswordPages.url)
        self.reset_password_step1(self.user.email)
        reset_password_link = re.search(
            r"(https?://.+/reset/.+/.+/)", mail.outbox[0].body
        )
        self.assertIsNotNone(
            reset_password_link,
            "Reset password link should be present in password reset email",
        )

        # He click on the password reset link and is invited to set its new password
        self.visit(reset_password_link.group(1), absolute_url=True)
        self.assertIn("new password", self.head_title)

        # User set is new password
        new_password = "reset_a123456!"
        self.reset_password_step2(new_password)
        self.assertIn(
            "Your password has been set",
            self.get_elem_text(self.login_messages),
            "A confirmation message should tell user than he can login now",
        )

        # User is not able to login using its old password
        self.visit(LoginPage.url)
        self.log_user()
        self.assertIn(
            "email address and password",
            self.get_elem_text(self.login_failed_div),
            "User login should failed using its old password",
        )

        # User is able to login using its new password
        self.log_user(password=new_password)
        self.assertIn("home", self.head_title)
