#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage


class ResetPasswordPages(BasePage):
    url = "/password_reset/"

    page_title = "h1"

    # Step 1/2 (receive email)
    email_input = "#password-reset-form #id_email"
    submit_email_input = '#password-reset-form [type="submit"]'
    confirmation_message = ""

    # Step 2/2 (set new password)
    new_password_input = "#password-reset-confirm #id_new_password1"
    confirm_password_input = "#password-reset-confirm #id_new_password2"
    submit_new_password_input = '#password-reset-confirm [type="submit"]'

    def reset_password_step1(self, email):
        email_input = self.get_elem(self.email_input)
        submit_input = self.get_elem(self.submit_email_input)

        email_input.send_keys(email)
        submit_input.click()

    def reset_password_step2(self, new_password):
        new_password_input = self.get_elem(self.new_password_input)
        confirm_password_input = self.get_elem(self.confirm_password_input)
        submit_input = self.get_elem(self.submit_new_password_input)

        new_password_input.send_keys(new_password)
        confirm_password_input.send_keys(new_password)
        submit_input.click()
