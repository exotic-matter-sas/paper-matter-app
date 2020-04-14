#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class AdminHomePage(BasePage):
    url = "/admin/"

    page_title = "h1"

    create_org_link = ".model-ftlorg a.addlink"
    org_name_input = "#id_name"
    org_slug_input = "#id_slug"
    org_submit_input = 'input[type="submit"].default'

    def create_org(self, name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1):
        org_name_input = self.get_elem(self.org_name_input)
        org_slug_input = self.get_elem(self.org_slug_input)
        org_submit_input = self.get_elem(self.org_submit_input)

        org_name_input.send_keys(name)
        org_slug_input.send_keys(slug)
        org_submit_input.click()

        return slug
