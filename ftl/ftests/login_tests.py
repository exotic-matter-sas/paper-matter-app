from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class LoginPageTests(LoginPage, HomePage):
    def test_first_user_can_login(self):
        """First user can login and access a logged page"""
        # Admin user have already setup org and admin
        org = setup_org()
        setup_admin(org=org)
        # User have already created its account
        user = setup_user(org=org)

        # User login and is redirect to the logged home page
        self.visit(self.url)
        self.log_user(1)

        # He can see it's username on it
        self.assertIn('home', self.head_title)
        self.assertIn(user.username, self.get_elem(self.profile_name).text)
