#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class SetupPages(BasePage):
    create_org_url = "/setup/createorg/"
    create_admin_url = "/setup/create_admin/"
    setup_completed_url = "/setup/success/"

    breadcrumb = ".breadcrumb"
    active_breadcrumb_item = ".breadcrumb .active"

    admin_org_name_input = "#admin-form #id_org_name"
    admin_email_address_input = "#admin-form #id_email"
    admin_password_input = "#admin-form #id_password1"
    admin_password_confirmation_input = "#admin-form #id_password2"
    admin_submit_input = '#admin-form [type="submit"]'
    # Setup completed
    admin_login_link = "#admin-login"
    user_signup_link = "#user-signup"

    def create_first_org_and_admin(self):
        org_name_input = self.get_elem(self.admin_org_name_input)
        email_address_input = self.get_elem(self.admin_email_address_input)
        password_input = self.get_elem(self.admin_password_input)
        password_confirmation_input = self.get_elem(
            self.admin_password_confirmation_input
        )
        submit_input = self.get_elem(self.admin_submit_input)

        org_name_input.send_keys(tv.ORG_NAME_1)
        email_address_input.send_keys(tv.ADMIN1_EMAIL)
        password_input.send_keys(tv.ADMIN1_PASS)
        password_confirmation_input.send_keys(tv.ADMIN1_PASS)
        submit_input.click()
