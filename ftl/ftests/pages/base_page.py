#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import json
import os
import platform
import secrets
import time
from tempfile import TemporaryDirectory
from unittest import SkipTest

from celery import shared_task
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import LiveServerTestCase, tag
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

import ftests.tools.detect_server as server

if "CI" in os.environ:
    LIVE_SERVER = LiveServerTestCase
else:
    # Use StaticLiveServerTestCase when test running locally to not depend on collectstatic run
    LIVE_SERVER = StaticLiveServerTestCase


@tag("slow")
class BasePage(LIVE_SERVER):
    modal_input = ".modal-dialog input[type='text']"
    modal_accept_button = ".modal-dialog .modal-footer .btn-primary, .modal-dialog .modal-footer .btn-danger"
    modal_reject_button = ".modal-dialog .modal-footer .btn-secondary"
    modal_close_button = ".modal-dialog .close"

    notification = ".b-toaster-slot .b-toast"
    success_notification = ".b-toaster-slot .b-toast-success"
    error_notification = ".b-toaster-slot .b-toast-danger"
    close_notification = ".b-toaster-slot .b-toast .close"

    loader = ".loader"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_url = ""
        self.expected_browser_logs = []

        self._download_dir = None
        self._tests_screenshots_path = os.path.join(
            settings.BASE_DIR, "ftests", "tests_screenshots"
        )
        self._browser_logs_path = os.path.join(
            settings.BASE_DIR, "ftests", "browser_logs"
        )

    @classmethod
    def setUpClass(cls):
        if (
            settings.DEV_MODE
            and "CI" not in os.environ
            and not server.Node.is_running()
        ):
            raise SkipTest("Node server not running, skipping Ftest")
        super().setUpClass()

    def setUp(self, browser=settings.DEFAULT_TEST_BROWSER, browser_locale="en"):
        self._download_dir = TemporaryDirectory()

        if browser == "firefox":
            profile = webdriver.FirefoxProfile()
            # Set browser language for web pages
            profile.set_preference("intl.accept_languages", browser_locale)

            # Set default browser download dir and remove download prompt
            profile.set_preference("browser.download.dir", self._download_dir.name)
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            mime_type_list = "application/octet-stream"
            profile.set_preference(
                "browser.helperApps.neverAsk.openFile", mime_type_list
            )
            profile.set_preference(
                "browser.helperApps.neverAsk.saveToDisk", mime_type_list
            )

            options = FirefoxOptions()
            if settings.TEST_BROWSER_HEADLESS:
                options.headless = True
            if settings.BROWSER_BINARY_PATH:
                options.binary_location = settings.BROWSER_BINARY_PATH

            self.browser = webdriver.Firefox(
                executable_path=settings.DEFAULT_GECKODRIVER_PATH,
                firefox_profile=profile,
                firefox_options=options,
            )
        elif browser == "chrome":
            options = ChromeOptions()
            # --lang argument is no more supported on Linux
            # see: https://bugs.chromium.org/p/chromium/issues/detail?id=755338#c14
            if platform.system() == "Linux":
                os.environ["LANGUAGE"] = browser_locale
            else:
                options.add_argument(f"--lang={browser_locale}")

            # Set default browser download dir and remove download prompt
            chrome_profile = {
                "download.default_directory": self._download_dir.name,
                "savefile.default_directory": self._download_dir.name,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }

            if settings.TEST_BROWSER_HEADLESS:
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                if platform.system() == "Windows":  # Needed due to Chrome bug
                    options.add_argument("--disable-gpu")
            if settings.BROWSER_BINARY_PATH:
                options.binary_location = settings.BROWSER_BINARY_PATH

            options.add_experimental_option("prefs", chrome_profile)
            self.browser = webdriver.Chrome(
                executable_path=settings.DEFAULT_CHROMEDRIVER_PATH,
                chrome_options=options,
            )
        else:
            raise ValueError("Unsupported browser, allowed: firefox, chrome")

        # Set a default window size
        self.browser.set_window_size(1366, 768)
        # Set default timeout
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self._download_dir.cleanup()
        self._save_browser_logs()

        self.browser.quit()

    def _save_browser_logs(self):
        # get_log only work with Chrome (see note in https://gitlab.com/exotic-matter/ftl-app/-/issues/203)
        if self.browser.name in ["chrome", "chromium"]:
            browser_logs = {
                "expected": self.expected_browser_logs,
                "actual": self.browser.get_log("browser"),
            }
            if len(browser_logs["actual"]) or len(browser_logs["expected"]):
                file_path = os.path.join(
                    self._browser_logs_path, f"{self.id()}-{int(time.time())}.json"
                )
                with open(file_path, "w") as f:
                    f.write(json.dumps(browser_logs))
        self.expected_browser_logs.clear()

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
        self.browser.save_screenshot(
            os.path.join(
                self._tests_screenshots_path, f"{self.id()}-{int(time.time())}.png"
            )
        )

    def get_elem(self, css_selector, is_visible=True):
        elem = self.browser.find_element_by_css_selector(css_selector)
        if elem.is_displayed() == is_visible:
            return elem
        else:
            raise NoSuchElementException(msg=f"{css_selector} not found")

    def get_elems(self, css_selector, is_visible=True):
        elems = self.browser.find_elements_by_css_selector(css_selector)
        if elems and elems[0].is_displayed() == is_visible:
            return elems
        else:
            raise NoSuchElementException(msg=f"{css_selector} not found")

    def get_elem_text(
        self, css_selector, is_visible=True, web_element_instead_of_css_selector=False
    ):
        elem = (
            css_selector
            if web_element_instead_of_css_selector
            else self.get_elem(css_selector, is_visible)
        )

        if elem.tag_name == "input":
            return elem.get_attribute("value")
        elif elem.tag_name == "select":
            return elem.find_element_by_css_selector("option:checked").text
        else:
            return elem.text

    def get_elems_text(self, css_selector, is_visible=True):
        elems_text = []
        elems = self.browser.find_elements_by_css_selector(css_selector)

        if elems and elems[0].is_displayed() == is_visible:
            for elem in elems:
                elems_text.append(
                    self.get_elem_text(
                        elem, is_visible, web_element_instead_of_css_selector=True
                    )
                )
            return elems_text
        else:
            raise NoSuchElementException(msg=f"{css_selector} not found")

    def get_elem_attribute(self, css_selector, attribute_name, is_visible=True):
        elem = self.get_elem(css_selector, is_visible)

        return elem.get_attribute(attribute_name)

    @staticmethod
    def _wait_for_method_to_return(
        method,
        timeout,
        *method_args,
        custom_return_validator=None,
        expected_exception_types=(),
        **method_kwargs,
    ):
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

    def _wait_for_method_to_raise_exception(
        self, method, timeout, exception_types, *method_args, **method_kwargs
    ):
        # Use always False validator to only return if expected condition is raised
        def function(val):
            return False

        self._wait_for_method_to_return(
            method,
            timeout,
            *method_args,
            **method_kwargs,
            custom_return_validator=function,
            expected_exception_types=exception_types,
        )

    def wait_for_elem_to_show(self, css_selector, timeout=2):
        WebDriverWait(self.browser, timeout).until(
            Ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_for_elem_to_disappear(self, css_selector, timeout=2):
        try:
            self._wait_for_method_to_raise_exception(
                self.get_elem,
                timeout,
                (NoSuchElementException, StaleElementReferenceException),
                css_selector,
            )
        except TimeoutException:
            raise TimeoutException(
                f'The element "{css_selector}" doesn\'t disapear after {timeout}s'
            )

    def wait_for_elem_text_to_be_valid(self, css_selector, validator, timeout=2):
        try:
            self._wait_for_method_to_return(
                self.get_elem_text,
                timeout,
                css_selector,
                True,
                custom_return_validator=validator,
            )
        except TimeoutException:
            raise TimeoutException(
                f'The element text "{css_selector}" doesn\'t turn to be valid after {timeout}s'
            )

    def wait_for_elem_text_to_be(self, css_selector, elem_text, timeout=2):
        validator = lambda text: True if text == elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def wait_for_elem_text_not_to_be(self, css_selector, elem_text, timeout=2):
        validator = lambda text: True if text != elem_text else False
        self.wait_for_elem_text_to_be_valid(css_selector, validator, timeout)

    def wait_celery_queue_to_be_empty(self, celery_worker, timeout=60):
        rand_pid = secrets.token_hex(32)

        def return_counter():
            if rand_pid in celery_worker.stats()["total"]:
                return celery_worker.stats()["total"][rand_pid]
            else:
                return 0

        def celery_waiter_return_validator(count):
            return count == 1

        dummy_task_for_test.apply_async(shadow=rand_pid)
        # Wait for a celery worker to have processed our dummy task, meaning it has processed all previous tasks.
        # This assumes the worker has only one process.
        self._wait_for_method_to_return(
            return_counter,
            timeout,
            custom_return_validator=celery_waiter_return_validator,
        )

    def close_all_notifications(self):
        self.wait_for_elem_to_show(self.close_notification)
        notification_to_close = self.get_elems(self.close_notification)
        for notification in notification_to_close:
            notification.click()
        self.wait_for_elem_to_disappear(self.notification)

    def _finish_test_reminder(self, message="Finish test!", pause_test=False):
        red_message = "\x1b[1;31m{}\033[0m"
        print(red_message.format(message))

        if pause_test:
            input(f"Test paused for debugging, press Enter to terminate")
        self.fail(message)

    def accept_modal(self):
        self.wait_for_elem_to_show(self.modal_accept_button)
        time.sleep(0.5)
        self.get_elem(self.modal_accept_button).click()
        self.wait_for_elem_to_disappear(self.modal_accept_button)

    @staticmethod
    def get_last_email():
        return mail.outbox[-1]

    def download_file(self, download_trigger_css_selector, timeout=10):
        initial_content = os.listdir(self._download_dir.name)
        self.get_elem(download_trigger_css_selector).click()
        current_content = initial_content

        # Wait for new file to show up in download dir
        start_time = time.time()
        while len(initial_content) == len(current_content):
            if time.time() - start_time > timeout:
                raise TimeoutException(f"No file downloaded after {timeout}s")
            time.sleep(0.2)
            current_content = [
                e
                for e in os.listdir(self._download_dir.name)
                if not e.endswith((".crdownload", ".tmp", "."))
            ]

        downloaded_filename = (set(current_content) - set(initial_content)).pop()
        return downloaded_filename

    def drag_n_drop_elem(self, elem_to_drag, elem_drop_zone):
        # ActionChains(self.browser).drag_and_drop(elem_to_drag, elem_drop_zone)
        # A work around is needed to perform a drag n drop with selenium due to a bug:
        # https://github.com/SeleniumHQ/selenium/issues/8003

        with open(
            os.path.join(
                settings.BASE_DIR, "ftests", "tools", "drag_n_drop_workaround.js"
            ),
            mode="r",
        ) as js_file:
            js_to_execute = js_file.read()
            self.browser.execute_script(js_to_execute, elem_to_drag, elem_drop_zone)

    def select_dropdown_option(self, select_css_selector, option_to_select_text):
        Select(self.get_elem(select_css_selector)).select_by_visible_text(
            option_to_select_text
        )


@shared_task
def dummy_task_for_test():
    pass
