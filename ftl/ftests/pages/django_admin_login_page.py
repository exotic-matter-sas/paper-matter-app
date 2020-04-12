#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class AdminLoginPage(BasePage):
    url = "/admin/"

    page_title = "h2"

    admin_login_email_input = "#login-form #id_username"
    admin_login_password_input = "#login-form #id_password"
    admin_login_submit_input = '#login-form [type="submit"]'

    django_admin_success_message = "#user-tools"

    def log_admin(self):
        email_input = self.get_elem(self.admin_login_email_input)
        password_input = self.get_elem(self.admin_login_password_input)
        submit_input = self.get_elem(self.admin_login_submit_input)

        email_input.send_keys(tv.ADMIN_EMAIL)
        password_input.send_keys(tv.ADMIN_PASS)
        submit_input.click()
