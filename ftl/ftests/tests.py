from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document
from ftests.pages.base_page import BasePage


class LoginPageTests(BasePage):
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


class HomePageTests(BasePage):
    def setUp(self, **kwargs):
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.browser.implicitly_wait(5)
        self.browser.get(f'{self.live_server_url}/login')
        self.log_user('user1')

    def test_user_can_display_document(self):
        """Logged user can display a document"""
        setup_document(self.org, self.user)
        self.refresh_document_list()

        # User click on the first listed document
        self.open_first_document()
        # User can see the pdf inside the pdf viewer
        pdf_viewer_iframe = self.browser.find_element_by_css_selector('.doc-view-modal iframe')
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.browser.find_element_by_css_selector('title').get_attribute("innerHTML")

        self.assertEqual(pdf_viewer_iframe_title, 'PDF.js viewer')


class I18nTests(BasePage):
    def setUp(self, browser=None, browser_locale='fr'):
        super().setUp(browser_locale='fr')

    def test_i18n_are_working(self):
        """First user can login and access a logged page"""
        # Admin, organization and user setup
        self.browser.get(self.live_server_url)
        self.browser.implicitly_wait(5)
        self.assertIn('organisation', self.browser.find_elements_by_css_selector('h2')[0].text)
