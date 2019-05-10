from ftests.pages.setup_pages import SetupPages


class I18nTests(SetupPages):
    def setUp(self, browser=None, browser_locale='fr'):
        super().setUp(browser_locale='fr')

    def test_i18n_are_working(self):
        self.visit(self.root_url)
        self.assertIn('organisation', self.get_elem(self.page_title).text)
