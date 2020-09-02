#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class SignupPages(BasePage):
    url = "/signup/"
    page_title = "h1"
    main_panel = "#main-with-aside"

    # Signup form
    org_name_input = "#organization-form #id_org_name"
    email_address_input = "#organization-form #id_email"
    password_input = "#organization-form #id_password1"
    password_confirmation_input = "#organization-form #id_password2"
    submit_input = '#organization-form [type="submit"]'

    org_error_message = 'label[for="id_org_name"] + .errorlist'
    email_error_message = 'label[for="id_email"] + .errorlist'

    def create_user(self, user_num=1, activate_user=False):
        org_name_input = self.get_elem(self.org_name_input)
        email_address_input = self.get_elem(self.email_address_input)
        password_input = self.get_elem(self.password_input)
        password_confirmation_input = self.get_elem(self.password_confirmation_input)
        submit_input = self.get_elem(self.submit_input)

        org_name_input.send_keys(getattr(tv, f"ORG_NAME_{user_num}"))
        email = getattr(tv, f"USER{user_num}_EMAIL")
        email_address_input.send_keys(email)
        password_input.send_keys(getattr(tv, f"USER{user_num}_PASS"))
        password_confirmation_input.send_keys(getattr(tv, f"USER{user_num}_PASS"))
        submit_input.click()

        if activate_user:
            if getattr(self, "_worker", None):
                self.wait_celery_queue_to_be_empty(self._worker)

            activation_email = self.get_last_email()
            activation_url = re.search(
                r"(https?://.+/accounts/activate/.+/)", activation_email.body
            ).group(1)
            self.visit(activation_url, absolute_url=True)

        return email
