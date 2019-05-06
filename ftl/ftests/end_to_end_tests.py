from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.signup_pages import SignupPages
from ftests.pages.user_login_page import LoginPage


class SetupTest(SetupPages, SignupPages, LoginPage, HomePage):
    def test_end_to_end_setup(self):
        # Admin have just install ftl-app and display it for the first time
        self.visit(self.root_url)

        # Admin fulfill the org creation form
        self.create_first_organization()

        # Admin fulfill the admin creation form
        self.create_admin()

        # Admin copy the link for user signup and send it to the first user
        user_signup_link = self.get_elem(self.user_signup_link).get_attribute('href')

        # Admin close its browser
        self.browser.quit()

        # First user display the app for the first time using the link sent by Admin
        self.setUp()
        self.visit(user_signup_link, absolute_url=True)

        # First user fulfill the user creation form
        username = self.create_user()

        # First user login to the first organization
        self.get_elem(self.user_login_link).click()
        self.log_user()

        # First user is properly logged
        self.assertIn('home', self.head_title)
        self.assertIn(username, self.get_elem(self.profile_name).text)

