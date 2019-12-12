#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class SignupPages(BasePage):
    page_title = 'h1'
    main_panel = '#main-with-aside'

    # Signup form
    email_address_input = '#user-form #id_email'
    password_input = '#user-form #id_password1'
    password_confirmation_input = '#user-form #id_password2'
    submit_input = '#user-form [type="submit"]'

    def visit_signup_page(self, org_slug):
        self.visit(f'/signup/{org_slug}/')

    def create_user(self, user_num=1, activate_user=False):
        email_address_input = self.get_elem(self.email_address_input)
        password_input = self.get_elem(self.password_input)
        password_confirmation_input = self.get_elem(self.password_confirmation_input)
        submit_input = self.get_elem(self.submit_input)

        email = getattr(tv, f'USER{user_num}_EMAIL')
        email_address_input.send_keys(email)
        password_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        password_confirmation_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        submit_input.click()

        if activate_user:
            activation_email = self.get_last_email()
            activation_url = re.search(r'(https?://.+/accounts/activate/.+/)', activation_email.body).group(1)
            self.visit(activation_url, absolute_url=True)

        return email
