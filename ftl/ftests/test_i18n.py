#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from unittest import skipIf

from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import DEV_MODE


class I18nTests(SetupPages, LoginPage, HomePage):
    def setUp(self, browser=None, browser_locale='fr-fr, fr'):
        super().setUp(browser_locale=browser_locale)

    def test_i18n_are_working(self):
        self.visit(self.root_url)
        self.assertIn('administrateur', self.head_title,
                      '"administrator" should be translated as "administrateur"')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_js_i18n_are_working(self):
        # first org, admin, user are already created, user is already logged on home page
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

        self.visit(self.root_url)
        self.assertIn('Ajouter un document', self.get_elem(self.document_upload_label).text,
                      '"Upload document" should be translated as "Ajouter un document"')
