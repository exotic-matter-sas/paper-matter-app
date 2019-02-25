import platform
import os
import unittest

from selenium import webdriver

from ftl.ftl.settings import BASE_DIR
from ftl.functional_tests import test_values as TV


class LandingPageTest(unittest.TestCase):

    def setUp(self):
        if platform.system().startswith('Linux'):
            executable_path = 'functional_tests/geckodriver/geckodriver64_linux'
        elif platform.system().startswith('Windows'):
            executable_path = 'functional_tests/geckodriver/geckodriver64.exe'
        elif platform.system().startswith('Darwin'):
            executable_path = 'functional_tests/geckodriver/geckodriver64_linux'
        else:
            raise EnvironmentError(f'Platform "{platform.system()}" not supported')

        self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path))

    def tearDown(self):
        self.browser.quit()

    def test_a_landing_page_display_properly_on_first_visit(self):
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get('http://localhost:8000')

        # A landing page welcome the user and ask him to set admin first organisation information
        self.assertIn('Ftl-app', self.browser.title)
        self.assertIn('Admin creation', self.browser.find_elements_by_css_selector('h2')[0].text)
        self.assertIn('First organization creation', self.browser.find_elements_by_css_selector('h2')[1].text)

    def test_b_landing_page_admin_and_first_organization_creation(self):
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get('http://localhost:8000')
        # He fulfill the admin creation form and first organization
        admin_form = self.browser.find_element_by_id('admin-form')
        email_address_input = admin_form.find_element_by_id('id_email')
        password_input = admin_form.find_element_by_id('id_password')
        submit_input = admin_form.find_element_by_css_selector('[type="submit"]')

        email_address_input.send_keys(TV.ADMIN_EMAIL)
        password_input.send_keys(TV.ADMIN_PASS)
        submit_input.click()

        # TODO add tests for organization form

        # A success page mention the urls for admin and user signup page
        self.assertIn('Setup completed', self.browser.title)
        admin_login_link = self.browser.find_element_by_id('admin-login')
        self.assertIn('/admin', admin_login_link.get_attribute('href'))

        user_signup_link = self.browser.find_element_by_id('user-login')
        self.assertIn('/signup', user_signup_link.get_attribute('href'))

        # Display ftl-app again now redirect to user login page
        self.browser.get('http://localhost:8000')
        self.assertIn('Login', self.browser.title)

        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main()
