#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
import platform
import time
import urllib.error
import urllib.request
from tempfile import TemporaryDirectory

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import LiveServerTestCase, tag
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait


if 'CI' in os.environ:
    LIVE_SERVER = LiveServerTestCase
else:
    # Use StaticLiveServerTestCase when test running locally to not depend on collectstatic run
    LIVE_SERVER = StaticLiveServerTestCase


def is_node_server_running():
    """
    Check if Node server is running
    """
    if settings.DEV_MODE and 'CI' not in os.environ:
        try:
            urllib.request.urlopen('http://localhost:8080/')
            return True
        except urllib.error.URLError:
            return False
    else:
        return False


# Display a warning if Node server not running during test execution
NODE_SERVER_RUNNING = is_node_server_running()
red_message = '\x1b[1;31m{}\033[0m'
if settings.DEV_MODE and not is_node_server_running() and 'CI' not in os.environ:
    print(red_message.
          format('WARNING: Node server NOT running: all tests related to JS frontend will be skipped.'))
    input("Run Node server now if you want to run all tests, press Enter to continue...")
    NODE_SERVER_RUNNING = is_node_server_running()  # refresh value in case user hae just run Node
    print(f'Continue with NODE_SERVER_RUNNING: {NODE_SERVER_RUNNING}')


@tag('slow')
class BasePage(LIVE_SERVER):
    modal_input = '.modal-dialog input'
    modal_accept_button = '.modal-dialog .modal-footer .btn-primary, .modal-dialog .modal-footer .btn-danger'
    modal_reject_button = '.modal-dialog .modal-footer .btn-secondary'

    notification = '.b-toaster-slot .b-toast'
    success_notification = '.b-toaster-slot .b-toast-success'
    error_notification = '.b-toaster-slot .b-toast-danger'
    close_notification = '.b-toaster-slot .b-toast .close'

    loader = '.loader'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_url = ''

        self._download_dir = None
        self._tests_screenshots_path = os.path.join(settings.BASE_DIR, 'ftests', 'tests_screenshots')

    def setUp(self, browser=settings.DEFAULT_TEST_BROWSER, browser_locale='en'):
        self._download_dir = TemporaryDirectory()

        if browser == 'firefox':
            profile = webdriver.FirefoxProfile()
            # Set browser language for web pages
            profile.set_preference('intl.accept_languages', browser_locale)

            # Set default browser download dir and remove download prompt
            profile.set_preference('browser.download.dir', self._download_dir.name)
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            mime_type_list = 'application/octet-stream'
            profile.set_preference('browser.helperApps.neverAsk.openFile', mime_type_list)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', mime_type_list)

            options = FirefoxOptions()
            if settings.TEST_BROWSER_HEADLESS:
                options.headless = True
            if settings.BROWSER_BINARY_PATH:
                options.binary_location = settings.BROWSER_BINARY_PATH

            self.browser = webdriver.Firefox(executable_path=settings.DEFAULT_GECKODRIVER_PATH, firefox_profile=profile,
                                             firefox_options=options)
        elif browser == 'chrome':
            options = ChromeOptions()
            # Set browser language for web pages
            options.add_argument(f'--lang={browser_locale}')

            # Set default browser download dir and remove download prompt
            chrome_profile = {
                'download.default_directory': self._download_dir.name,
                'savefile.default_directory': self._download_dir.name, 'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'profile.default_content_setting_values.automatic_downloads': 1
            }

            if settings.TEST_BROWSER_HEADLESS:
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                if platform.system() == 'Windows':  # Needed due to Chrome bug
                    options.add_argument('--disable-gpu')
            if settings.BROWSER_BINARY_PATH:
                options.binary_location = settings.BROWSER_BINARY_PATH

            options.add_experimental_option('prefs', chrome_profile)
            self.browser = webdriver.Chrome(executable_path=settings.DEFAULT_CHROMEDRIVER_PATH, chrome_options=options)
        else:
            raise ValueError('Unsupported browser, allowed: firefox, chrome')

        # Set a default window size
        self.browser.set_window_size(1024, 768)
        # Set default timeout
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self._download_dir.cleanup()

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

    """
    For debug purpose
    """
    def screenshot_page(self):
        self.browser.save_screenshot(os.path.join(self._tests_screenshots_path, f'{self.id()}-{int(time.time())}.png'))

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

    def get_elem_text(self, css_selector, is_visible=True, web_element_instead_of_css_selector=False):
        elem = css_selector if web_element_instead_of_css_selector else self.get_elem(css_selector, is_visible)

        if elem.tag_name == 'input':
            return elem.get_attribute('value')
        elif elem.tag_name == 'select':
            return elem.find_element_by_css_selector('option:checked').text
        else:
            return elem.text

    def get_elems_text(self, css_selector, is_visible=True):
        elems_text = []
        elems = self.browser.find_elements_by_css_selector(css_selector)

        if elems and elems[0].is_displayed() == is_visible:
            for elem in elems:
                elems_text.append(
                    self.get_elem_text(elem, is_visible, web_element_instead_of_css_selector=True)
                )
            return elems_text
        else:
            raise NoSuchElementException()

    @staticmethod
    def _wait_for_method_to_return(method, timeout, *method_args, custom_return_validator=None,
                                   expected_exception_types=(), **method_kwargs):
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

    def wait_for_elem_to_show(self, css_selector, timeout=2):
        WebDriverWait(self.browser, timeout).until(
            Ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_for_elem_to_disappear(self, css_selector, timeout=2):
        try:
            self._wait_for_method_to_raise_exception(self.get_elem, timeout,
                                                     (NoSuchElementException, StaleElementReferenceException),
                                                     css_selector)
        except TimeoutException:
            raise TimeoutException(f'The element "{css_selector}" doesn\'t disapear after {timeout}s')

    def wait_for_elem_text_to_be_valid(self, css_selector, validator, timeout=2):
        try:
            self._wait_for_method_to_return(self.get_elem_text, timeout, css_selector, True,
                                            custom_return_validator=validator)
        except TimeoutException:
            raise TimeoutException(f'The element text "{css_selector}" doesn\'t turn to be valid after {timeout}s')

    def wait_for_elem_text_to_be(self, css_selector, elem_text, timeout=2):
        validator = lambda text: True if text == elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def wait_for_elem_text_not_to_be(self, css_selector, elem_text, timeout=2):
        validator = lambda text: True if text != elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def close_all_notifications(self):
        self.wait_for_elem_to_show(self.close_notification)
        notification_to_close = self.get_elems(self.close_notification)
        for notification in notification_to_close:
            notification.click()
        self.wait_for_elem_to_disappear(self.notification)

    def _finish_test_reminder(self, message='Finish test!', pause_test=False):
        print(red_message.
              format(message))

        if pause_test:
            input(f'Test paused for debugging, press Enter to terminate')
        self.fail(message)

    def accept_modal(self):
        self.wait_for_elem_to_show(self.modal_accept_button)
        self.get_elem(self.modal_accept_button).click()
        self.wait_for_elem_to_disappear(self.modal_accept_button)

    @staticmethod
    def get_last_email():
        return mail.outbox[-1]

    def download_file(self, download_trigger_css_selector, timeout=10):
        self.get_elem(download_trigger_css_selector).click()
        initial_content = os.listdir(self._download_dir.name)
        current_content = initial_content

        # Wait for new file to show up in download dir
        start_time = time.time()
        while len(initial_content) == len(current_content):
            if time.time() - start_time > timeout:
                raise TimeoutException(f'No file downloaded after {timeout}s')
            time.sleep(0.2)
            current_content = [e for e in os.listdir(self._download_dir.name)
                               if not e.endswith(('.crdownload', '.tmp', '.'))]

        downloaded_filename = (set(current_content) - set(initial_content)).pop()
        return downloaded_filename
