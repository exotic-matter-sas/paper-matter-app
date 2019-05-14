from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class I18nTests(SetupPages, LoginPage, HomePage):
    def setUp(self, browser=None, browser_locale='fr'):
        super().setUp(browser_locale='fr')

    def test_i18n_are_working(self):
        self.visit(self.root_url)
        self.assertIn('organisation', self.get_elem(self.page_title).text)

    def test_js_i18n_are_working(self):
        # first org, admin, user are already created, user is already logged on home page
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

        self.visit(self.root_url)
        self.assertIn('fichier', self.get_elem(self.document_upload_label).text)
