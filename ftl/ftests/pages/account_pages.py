#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage


class AccountPages(BasePage):
    index_url = '/accounts/'
    update_email_url = '/accounts/email'
    update_password_url = '/accounts/password'

    success_notification = '.alert.alert-success'
    error_notification = '.alert.alert-error'

    page_title = 'h3'

    # Change email page
    new_email_input = '#email-update-form #id_email'
    submit_new_email_input = '#email-update-form [type="submit"]'

    # Change password page
    old_password_input = '#password-update-form #id_old_password'
    new_password_input = '#password-update-form #id_new_password1'
    new_password_confirmation_input = '#password-update-form #id_new_password2'
    submit_new_password_input = '#password-update-form [type="submit"]'

    def update_email(self, new_email):
        self.get_elem(self.new_email_input).send_keys(new_email)
        self.get_elem(self.submit_new_email_input).click()

    def update_password(self, old_password, new_password):
        self.get_elem(self.old_password_input).send_keys(old_password)
        self.get_elem(self.new_password_input).send_keys(new_password)
        self.get_elem(self.new_password_confirmation_input).send_keys(new_password)
        self.get_elem(self.submit_new_password_input).click()
