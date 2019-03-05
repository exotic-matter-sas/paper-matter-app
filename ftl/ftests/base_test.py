import platform
import os
from string import digits

from selenium import webdriver
from django.test import LiveServerTestCase

from ftl.settings import BASE_DIR
from ftests import _test_values as tv


class BaseTestCase(LiveServerTestCase):

    def setUp(self):
        if platform.system().startswith('Linux'):
            executable_path = 'ftests/geckodriver/geckodriver64_linux'
        elif platform.system().startswith('Windows'):
            executable_path = 'ftests/geckodriver/geckodriver64.exe'
        elif platform.system().startswith('Darwin'):
            executable_path = 'ftests/geckodriver/geckodriver64_linux'
        else:
            raise EnvironmentError(f'Platform "{platform.system()}" not supported')

        self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path))

    def tearDown(self):
        self.browser.quit()

    def create_user(self, user_type):
        # Remove counter at the end of user-type if needed
        user_selector = user_type[0:-1] if user_type[-1] in digits else user_type

        admin_form = self.browser.find_element_by_id(f'{user_selector}-form')
        username_input = admin_form.find_element_by_id('id_username')
        email_address_input = admin_form.find_element_by_id('id_email')
        password_input = admin_form.find_element_by_id('id_password1')
        password_confirmation_input = admin_form.find_element_by_id('id_password2')
        submit_input = admin_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(getattr(tv, f'{user_type.upper()}_USERNAME'))
        email_address_input.send_keys(getattr(tv, f'{user_type.upper()}_EMAIL'))
        password_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        password_confirmation_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        submit_input.click()

    def create_first_organization(self):
        organization_form = self.browser.find_element_by_id('organization-form')
        name_input = organization_form.find_element_by_id('id_name')
        slug_input = organization_form.find_element_by_id('id_slug')
        submit_input = organization_form.find_element_by_css_selector('[type="submit"]')

        name_input.send_keys(tv.ORG_NAME)
        slug_input.send_keys(tv.ORG_SLUG)
        submit_input.click()

    def select_org(self, org_slug):
        org_select_form = self.browser.find_element_by_id('organization-selection-form')
        org_slug_input = org_select_form.find_element_by_id('id_organization_slug')
        submit_input = org_select_form.find_element_by_css_selector('[type="submit"]')

        org_slug_input.send_keys(org_slug)
        submit_input.click()

    def log_user(self, user_type):
        login_form = self.browser.find_element_by_id('login-form')
        username_input = login_form.find_element_by_id('id_username')
        password_input = login_form.find_element_by_id('id_password')
        submit_input = login_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(getattr(tv, f'{user_type.upper()}_USERNAME'))
        password_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        submit_input.click()
