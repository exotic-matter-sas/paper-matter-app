from unittest import skip

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from .base_test import BaseTestCase


class LandingPageTests(BaseTestCase):
    def test_landing_page_display_properly_on_first_visit(self):
        """Landing page display properly on first visit"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # The landing page welcome the user and ask him to complete 1st step : org creation
        self.assertIn('Ftl-app', self.browser.title)
        self.assertIn('organization', self.browser.find_elements_by_css_selector('h2')[0].text)

    def test_landing_page_display_properly_after_admin_creation(self):
        """Landing page display properly after admin creation"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # He fulfill the org creation form and close his browser
        self.create_first_organization()
        self.browser.quit()

        # He come back later and display ftl-app again
        self.setUp()
        self.browser.get(self.live_server_url)

        # The landing page welcome the user and ask him to complete 2nd step : first organization creation
        self.assertIn('Ftl-app', self.browser.title)
        self.assertIn('administrator', self.browser.find_elements_by_css_selector('h2')[0].text)

    def test_landing_page_redirect_to_user_login_when_setup_complete(self):
        """Landing page redirect to user login page when setup complete"""
        # Display ftl-app now redirect to user login page
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # And then the first organisation form
        self.create_first_organization()

        # Create admin user
        self.create_user('admin')

        # A success page appears mentioning the urls for admin login page and user signup page
        self.assertIn('Setup completed', self.browser.title)
        admin_login_link = self.browser.find_element_by_id('admin-login')
        self.assertIn('/admin', admin_login_link.get_attribute('href'))

        user_signup_link = self.browser.find_element_by_id('user-signup')
        self.assertIn('/signup', user_signup_link.get_attribute('href'))

        # Display ftl-app again now redirect to user login page
        self.browser.get(self.live_server_url)
        self.assertIn('Login', self.browser.title)

    def test_admin_user_can_login_in_django_admin(self):
        """Admin user can login in Django admin"""
        setup_admin(setup_org())

        # Admin create first organization
        self.browser.get(self.live_server_url + "/admin")
        # self.create_first_organization()

        # He click on link to login to admin portal
        # admin_login_link = self.browser.find_element_by_id('admin-login')
        # admin_login_link.click()

        admin_login_form = self.browser.find_element_by_id('login-form')
        username_input = admin_login_form.find_element_by_id('id_username')
        password_input = admin_login_form.find_element_by_id('id_password')
        submit_input = admin_login_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(tv.ADMIN_USERNAME)
        password_input.send_keys(tv.ADMIN_PASS)
        submit_input.click()

        # Django admin display properly
        self.assertIn(f'welcome, {tv.ADMIN_USERNAME}', self.browser.find_element_by_id('user-tools').text.lower())

    def test_user_can_signup_to_first_organization(self):
        """User can signup to first organization"""
        # Admin create first organization
        self.browser.get(self.live_server_url)

        # And then the first organisation form
        self.create_first_organization()

        # Create admin user
        self.create_user('admin')

        # Admin copy the link for user signup and send it to the first user
        user_signup_link = self.browser.find_element_by_id('user-signup')

        # First user click on the link to signup to first organization
        user_signup_link.click()

        # The name of the first organization is displayed and user can create his account
        self.assertIn(tv.ORG_NAME, self.browser.find_element_by_css_selector('h1').text)
        self.create_user('user1')

        # Success message appears when account creation is complete
        self.assertIn('Congratulations', self.browser.find_element_by_css_selector('h1').text)

    def test_user_can_access_signup_page_of_first_organization(self):
        """User access signup page of first organization"""
        setup_admin(setup_org())

        # First user display signup page and signup to first organization
        self.browser.get(f'{self.live_server_url}/signup/{tv.ORG_SLUG}')
        self.create_user('user1')

        # He click on link to login
        user_login_link = self.browser.find_element_by_id('user-login')
        user_login_link.click()

        # The login page is displayed
        login_header = self.browser.find_element_by_css_selector('h1').text
        self.assertIn('login', login_header.lower())


class LoginPageTests(BaseTestCase):
    @skip('TODO Need a local node js server to be running, see https://gitlab.com/exotic-matter/ftl-app/issues/20')
    def test_first_user_can_login(self):
        """First user can login and access a logged page"""
        org = setup_org()
        setup_admin(org=org)
        setup_user(org=org)

        # User login and is redirect to the logged home page, he can see it's username on it
        self.browser.get(f'{self.live_server_url}/login')
        self.log_user('user1')

        element = WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'nav div em'), tv.USER1_USERNAME)
        )

        self.assertTrue(element)


class I18nTests(BaseTestCase):
    def setUp(self, browser=None, browser_locale='fr'):
        super().setUp(browser_locale='fr')

    def test_i18n_are_working(self):
        """First user can login and access a logged page"""
        # Admin, organization and user setup
        self.browser.get(self.live_server_url)
        self.browser.implicitly_wait(5)
        self.assertIn('organisation', self.browser.find_elements_by_css_selector('h2')[0].text)
