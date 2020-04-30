#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from selenium.webdriver.support.select import Select

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class AdminHomePage(BasePage):
    url = "/admin/"

    page_title = "h1"

    submit_input = 'input[type="submit"].default'

    create_org_link = ".model-ftlorg a.addlink"
    org_name_input = "#id_name"
    org_slug_input = "#id_slug"

    create_user_link = ".model-ftluser a.addlink"
    org_name_select = "#id_org"
    user_email_input = "#id_email"
    user_password_input = "#id_password1"
    user_password_confirmation_input = "#id_password2"
    user_staff_checkbox = "#id_is_staff"
    user_superuser_checkbox = "#id_is_superuser"

    def create_org(self, name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1):
        org_name_input = self.get_elem(self.org_name_input)
        org_slug_input = self.get_elem(self.org_slug_input)
        submit_input = self.get_elem(self.submit_input)

        org_name_input.send_keys(name)
        org_slug_input.send_keys(slug)
        submit_input.click()

        return slug

    def create_user(
        self,
        org_slug=tv.ORG_SLUG_1,
        email=tv.USER1_EMAIL,
        password=tv.USER1_PASS,
        is_admin=False,
    ):
        org_name_select = self.get_elem(self.org_name_select)
        user_email_input = self.get_elem(self.user_email_input)
        user_password_input = self.get_elem(self.user_password_input)
        user_password_confirmation_input = self.get_elem(
            self.user_password_confirmation_input
        )
        submit_input = self.get_elem(self.submit_input)

        Select(org_name_select).select_by_visible_text(org_slug)
        user_email_input.send_keys(email)
        user_password_input.send_keys(password)
        user_password_confirmation_input.send_keys(password)
        submit_input.click()

        if is_admin:
            user_staff_checkbox = self.get_elem(self.user_staff_checkbox)
            user_superuser_checkbox = self.get_elem(self.user_superuser_checkbox)
            submit_input = self.get_elem(self.submit_input)

            user_staff_checkbox.click()
            user_superuser_checkbox.click()
            submit_input.click()

        return email
