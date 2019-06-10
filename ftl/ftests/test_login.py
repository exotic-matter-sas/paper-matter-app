from unittest import skip, skipIf

from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import DEV_MODE


class LoginPageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created
        super().setUp()
        org = setup_org()
        setup_admin(org=org)
        # User have already created its account
        self.user = setup_user(org=org)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_first_user_can_login(self):
        """First user can login and access a logged page"""
        # User login and is redirected to the home page
        self.visit(LoginPage.url)
        self.log_user()

        # He can see it's username on it
        self.assertIn('home', self.head_title)
        self.assertIn(self.user.username, self.get_elem(self.profile_name).text)

    def test_login_failed(self):
        # User login and is redirect to the logged home page
        self.visit(LoginPage.url)
        self.log_user(user_num=2)  # User2 doesn't exist

        # User stay on login page and an error message is displayed
        self.assertIn('login', self.head_title)
        self.assertIn('Please enter a correct username and password', self.get_elem(self.login_failed_div).text)

    def test_login_page_redirect_logged_user(self):
        """First user can login and access a logged page"""
        # User login
        self.visit(LoginPage.url)
        self.log_user()

        # User access login page again
        self.visit(LoginPage.url)

        # User is redirected to home page as he is already logged
        self.assertIn('Home', self.browser.title)

    @skip('TODO when implemented in UI')  # TODO
    def test_password_forgotten(self):
        pass
