#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.setup_pages import SetupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_admin, setup_org


class LandingPageTests(SetupPages):
    def test_index_redirect_to_first_org_and_admin_creation_on_first_visit(self):
        """Index page redirect to first organization creation page on first visit"""
        # Admin user have just install app and display it for the first time
        self.visit(self.root_url)

        # The user is welcomed and asked to complete 1st setup step: org creation
        self.assertIn(tv.APP_NAME.lower(), self.head_title)
        self.assertIn("create first organization and administrator", self.head_title)

    def test_landing_page_redirect_to_user_login_when_setup_complete(self):
        """Landing page redirect to user login page when setup complete"""
        self.visit(self.root_url)

        # He fulfill the admin creation form
        self.create_first_org_and_admin()

        # A success page appears mentioning the urls for admin login page and user signup page
        self.assertIn("setup completed", self.head_title)
        self.assertIn(
            "/admin", self.get_elem(self.admin_login_link).get_attribute("href")
        )

        # Multi users feature disabled
        # self.assertIn('/signup', self.get_elem(self.user_signup_link).get_attribute('href'))

        # Display app again now redirect to user login page
        self.visit(self.root_url)
        self.assertIn("login", self.head_title)


class AdminLoginTests(LoginPage):
    def test_admin_user_can_login_in_django_admin(self):
        """Admin user can login in Django admin"""
        # Admin user have already setup org and admin
        setup_admin(setup_org())
        self.visit(LoginPage.admin_url)

        # He log to admin portal
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

        # Django admin display properly
        self.assertIn(
            f"welcome, {tv.ADMIN1_EMAIL}",
            self.get_elem(self.django_admin_success_message).text.lower(),
        )
