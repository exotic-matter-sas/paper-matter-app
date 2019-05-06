from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document


class HomePageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

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

