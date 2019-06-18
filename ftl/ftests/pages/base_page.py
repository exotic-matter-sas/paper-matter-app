import os
import platform
import time
import urllib.request
import urllib.error

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait

from ftl.settings import BASE_DIR, DEFAULT_TEST_BROWSER, TEST_BROWSER_HEADLESS, DEV_MODE

if 'CI' in os.environ:
    LIVE_SERVER = LiveServerTestCase
else:
    # Use StaticLiveServerTestCase when test running locally to not depend on collectstatic run
    LIVE_SERVER = StaticLiveServerTestCase


def is_node_server_running():
    """
    Check if Node server is running when launching ftests in DEV mode to display a warning
    """
    if DEV_MODE:
        try:
            urllib.request.urlopen('http://localhost:8080/')
            return True
        except urllib.error.URLError:
            return False


NODE_SERVER_RUNNING = is_node_server_running()
if DEV_MODE and not is_node_server_running():
    red_message = '\x1b[1;31m{}\033[0m'
    print(red_message.
          format('WARNING: Node server NOT running: all tests relative to JS frontend will be skipped.'))
    input("Run Node server now if you want all tests to be run, press Enter to continue...")
    NODE_SERVER_RUNNING = is_node_server_running()  # refresh value in case user hae just run Node
    print(f'Continue with NODE_SERVER_RUNNING: {NODE_SERVER_RUNNING}')


class BasePage(LIVE_SERVER):
    modal_input = '.modal-dialog input'
    modal_accept_button = '.modal-dialog .modal-footer .btn-primary'
    modal_reject_button = '.modal-dialog .modal-footer .btn-secondary'

    notification = '.b-toaster-slot .b-toast'
    success_notification = '.b-toaster-slot .b-toast-success'
    error_notification = '.b-toaster-slot .b-toast-danger'
    close_notification = '.b-toaster-slot .b-toast .close'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_url = ''

    def setUp(self, browser=DEFAULT_TEST_BROWSER, browser_locale='en'):
        platform_system = platform.system()

        if browser == 'firefox':
            if platform_system.startswith('Linux'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64_linux'
            elif platform_system.startswith('Windows'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64.exe'
            elif platform_system.startswith('Darwin'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64_macosx'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            profile = webdriver.FirefoxProfile()
            profile.set_preference('intl.accept_languages', browser_locale)

            options = FirefoxOptions()

            if TEST_BROWSER_HEADLESS:
                options.headless = True

            self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path),
                                             firefox_profile=profile, firefox_options=options)
        elif browser == 'chrome':
            if platform_system.startswith('Linux'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_linux64'
            elif platform_system.startswith('Windows'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_win32.exe'
            elif platform_system.startswith('Darwin'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_mac64'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            options = ChromeOptions()
            options.add_argument(f'--lang={browser_locale}')

            if TEST_BROWSER_HEADLESS:
                options.add_argument('--headless')
                if platform.system() == 'Windows':  # Needed due to Chrome bug
                    options.add_argument('--disable-gpu')

            self.browser = webdriver.Chrome(executable_path=os.path.join(BASE_DIR, chrome_driver_path),
                                            chrome_options=options)
        else:
            raise ValueError('Unsupported browser, allowed: firefox, chrome')

        # Set a default window size
        self.browser.set_window_size(1024, 768)
        # Set default timeout
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    @property
    def head_title(self):
        return self.browser.title.lower()

    def visit(self, url, absolute_url=False):
        if absolute_url:
            complete_url = url
        else:
            complete_url = self.live_server_url + url
        self.browser.get(complete_url)

    def previous_page(self, iteration=1):
        for _ in range(iteration):
            self.browser.back()

    def next_page(self, iteration=1):
        for _ in range(iteration):
            self.browser.forward()

    def refresh_page(self):
        self.browser.refresh()

    def get_elem(self, css_selector, is_visible=True):
        elem = self.browser.find_element_by_css_selector(css_selector)
        if elem.is_displayed() == is_visible:
            return elem
        else:
            raise NoSuchElementException()

    def get_elems(self, css_selector, is_visible=True):
        elems = self.browser.find_elements_by_css_selector(css_selector)
        if elems and elems[0].is_displayed() == is_visible:
            return elems
        else:
            raise NoSuchElementException()

    def get_elem_text(self, css_selector, is_visible=True):
        elem = self.get_elem(css_selector, is_visible)

        if elem.tag_name == 'input':
            return elem.get_attribute('value')
        elif elem.tag_name == 'select':
            return elem.find_element_by_css_selector('option:checked').text
        else:
            return elem.text

    @staticmethod
    def _wait_for_method_to_return(method, timeout, *method_args, custom_return_validator=None,
                                   expected_exception_types=None, **method_kwargs):
        """
        Wait for the given method to return a truthy value and return it
        If custom_return_validator is provided return value will be tested against the validator
        If expected_exception is provided and an exception of the provided type occurred return None
        """
        end_time = time.time() + timeout
        polling_interval = 0.5

        while True:
            try:
                value = method(*method_args, **method_kwargs)
                if custom_return_validator:
                    if custom_return_validator(value):
                        return value
                elif value:
                    return value

            except expected_exception_types:
                return None

            time.sleep(polling_interval)
            if time.time() > end_time:
                raise TimeoutException()

    def _wait_for_method_to_raise_exception(self, method, timeout, exception_types, *method_args, **method_kwargs):
        # Use always False validator to only return if expected condition is raised
        def function(val):
            return False

        self._wait_for_method_to_return(method, timeout, *method_args, **method_kwargs,
                                        custom_return_validator=function,
                                        expected_exception_types=exception_types)

    def wait_for_elem_to_show(self, css_selector, timeout=5):
        WebDriverWait(self.browser, timeout).until(
            Ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_for_elem_to_disappear(self, css_selector, timeout=5):
        try:
            self._wait_for_method_to_raise_exception(self.get_elem, timeout,
                                                     (NoSuchElementException, StaleElementReferenceException),
                                                     css_selector)
        except TimeoutException:
            raise TimeoutException(f'The element "{css_selector}" doesn\'t disapear after {timeout}s')

    def wait_for_elem_text_to_be_valid(self, css_selector, validator, timeout=5):
        try:
            self._wait_for_method_to_return(self.get_elem_text, timeout, css_selector, True,
                                            custom_return_validator=validator)
        except TimeoutException:
            raise TimeoutException(f'The element text "{css_selector}" doesn\'t turn to be valid after {timeout}s')

    def wait_for_elem_text_to_be(self, css_selector, elem_text, timeout=5):
        validator = lambda text: True if text == elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def wait_for_elem_text_not_to_be(self, css_selector, elem_text, timeout=5):
        validator = lambda text: True if text != elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def close_last_notification(self):
        self.wait_for_elem_to_show(self.notification)
        self.get_elem(self.close_notification).click()
        self.wait_for_elem_to_disappear(self.notification)
