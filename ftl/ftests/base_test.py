import os
import platform
from string import digits

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ftests import _test_values as tv
from ftl.settings import BASE_DIR


class BaseTestCase(LiveServerTestCase):

    def setUp(self, browser='firefox', browser_locale='en'):
        platform_system = platform.system()

        if browser == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference('intl.accept_languages', browser_locale)

            if platform_system.startswith('Linux'):
                executable_path = 'ftests/geckodriver/geckodriver64_linux'
            elif platform_system.startswith('Windows'):
                executable_path = 'ftests/geckodriver/geckodriver64.exe'
            elif platform_system.startswith('Darwin'):
                executable_path = 'ftests/geckodriver/geckodriver64_linux'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path),
                                             firefox_profile=profile)
        elif browser == 'chrome':
            if platform_system.startswith('Linux'):
                chrome_driver_path = 'ftests/chromedriver/chromedriver_linux64'
            elif platform_system.startswith('Windows'):
                chrome_driver_path = 'ftests/chromedriver/chromedriver_win32.exe'
            elif platform_system.startswith('Darwin'):
                chrome_driver_path = 'ftests/chromedriver/chromedriver_mac64'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            options = Options()
            options.add_argument("--lang={}".format(browser_locale))

            self.browser = webdriver.Chrome(executable_path=os.path.join(BASE_DIR, chrome_driver_path),
                                            chrome_options=options)
        else:
            raise ValueError('Unsupported browser, allowed: firefox, chrome')

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

    def log_user(self, user_type):
        login_form = self.browser.find_element_by_id('login-form')
        username_input = login_form.find_element_by_id('id_username')
        password_input = login_form.find_element_by_id('id_password')
        submit_input = login_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(getattr(tv, f'{user_type.upper()}_USERNAME'))
        password_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        submit_input.click()
