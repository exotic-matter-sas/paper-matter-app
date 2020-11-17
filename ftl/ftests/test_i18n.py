#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class I18nTests(SetupPages, LoginPage, HomePage):
    def setUp(self, browser=None, browser_locale="fr-FR, fr"):
        super().setUp(browser_locale=browser_locale)

    def test_i18n_are_working(self):
        self.visit(self.root_url)
        self.assertIn(
            "administrateur",
            self.head_title,
            '"administrator" should be translated as "administrateur"',
        )

    def test_js_i18n_are_working(self):
        # first org, admin, user are already created, user is already logged on home page
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

        self.visit(self.root_url)
        self.assertIn(
            "Ajouter des documents",
            self.get_elem_text(self.add_documents_button),
            '"Add documents" should be translated as "Ajouter des documents"',
        )
