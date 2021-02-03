#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

from ftests.pages.base_page import BasePage


class AccountPages(BasePage):
    index_url = "/accounts/"
    update_email_url = "/accounts/email/"
    update_password_url = "/accounts/password/"
    update_region_settings_url = "/accounts/settings/"
    two_factors_authentication_url = "/accounts/2fa/"
    delete_account_url = "/accounts/delete/"

    success_notification = ".alert.alert-success"
    error_notification = ".alert.alert-error"

    page_title = "h3"

    logout_button = 'a[href="/logout/"]'

    #################
    # User settings #
    #################

    # email page
    new_email_input = "#email-update-form #id_email"
    submit_new_email_input = '#email-update-form [type="submit"]'

    # password page
    old_password_input = "#password-update-form #id_old_password"
    new_password_input = "#password-update-form #id_new_password1"
    new_password_confirmation_input = "#password-update-form #id_new_password2"
    submit_new_password_input = '#password-update-form [type="submit"]'

    # region page
    language_select = "#account-settings-form #id_lang"
    timezone_select = "#account-settings-form #id_tz"
    submit_new_region_settings = '#account-settings-form [type="submit"]'

    ############
    # Security #
    ############

    # 2fa pages
    # static device
    emergency_codes_divs = ".static-device-item"
    add_emergency_codes_button = "#add-emergency-codes"
    rename_emergency_codes_buttons = ".rename-emergency-codes"
    delete_emergency_codes_buttons = ".delete-emergency-codes"
    emergency_codes_lists = "#emergency-code-to-print li, .static-device-item code"
    print_button = "#print_link"
    no_code_left_badges = ".otp-warning"
    # totp device
    auth_app_divs = ".totp-device-item"
    add_auth_app_button = "#add-auth-app"
    unconfirmed_badges = ".totp-device-item a.badge-danger"
    rename_auth_app_buttons = ".rename-auth-app"
    delete_auth_app_buttons = ".delete-auth-app"
    qr_code_image = 'img[src*="qrcode"]'
    # fido2 device
    security_key_divs = ".fido2-device-item"
    add_security_key_button = "#add-security-key"
    rename_security_key_buttons = ".rename-security-key"
    delete_security_key_buttons = ".delete-security-key"
    # 2fa forms
    device_name_label = 'label[for="id_name"]'
    device_name_input = "#id_name"
    error_message = ".alert-danger"
    cancel_button = ".btn-secondary, .btn-link"
    confirm_button = ".btn-primary, .btn-danger"
    delete_warning = ".text-danger"
    # 2fa check pages
    check_pages_title = "h1"
    check_pages_device_label = "form#user-form label"
    check_pages_device_input = "#id_otp_device"
    check_pages_device_select_options = "#id_otp_device option"
    check_pages_code_input = "#id_otp_token"
    # id_otp_device option
    check_pages_alternatives_list = "#alternatives-list li a"

    ##############
    # Management #
    ##############

    # Delete account page
    confirm_password_input = "#account-delete-form #password"
    submit_account_deletion = '#account-delete-form [type="submit"]'

    def update_email(self, new_email):
        self.get_elem(self.new_email_input).send_keys(new_email)
        self.get_elem(self.submit_new_email_input).click()

    def update_password(self, old_password, new_password):
        self.get_elem(self.old_password_input).send_keys(old_password)
        self.get_elem(self.new_password_input).send_keys(new_password)
        self.get_elem(self.new_password_confirmation_input).send_keys(new_password)
        self.get_elem(self.submit_new_password_input).click()

    def update_region_settings(self, language=None, timezone=None):
        if not (language or timezone):
            raise ValueError("You should set at least language and/or timezone param.")
        if language:
            self.select_dropdown_option(self.language_select, language)
        if timezone:
            self.select_dropdown_option(self.timezone_select, timezone)
        self.get_elem(self.submit_new_region_settings).click()

    def add_emergency_codes_set(self, codes_set_name):
        self.get_elem(self.add_emergency_codes_button).click()
        self.get_elem(self.device_name_input).send_keys(codes_set_name)
        self.get_elem(self.confirm_button).click()

    def rename_emergency_codes_set(self, new_name, set_index=0):
        self.get_elems(self.rename_emergency_codes_buttons)[set_index].click()
        self.wait_for_elem_to_disappear(self.rename_emergency_codes_buttons)
        self.get_elem(self.device_name_input).click()
        self.get_elem(self.device_name_input).send_keys(new_name)
        self.get_elem(self.confirm_button).click()
        self.wait_for_elem_to_disappear(self.device_name_input)

    def delete_emergency_codes_set(self, set_index=0):
        self.get_elems(self.delete_emergency_codes_buttons)[set_index].click()
        self.get_elem(self.confirm_button).click()

    def add_auth_app(self, device_name):
        self.get_elem(self.add_auth_app_button).click()
        self.get_elem(self.device_name_input).send_keys(device_name)
        self.get_elem(self.confirm_button).click()

    def rename_auth_app(self, new_name, set_index=0):
        self.get_elems(self.rename_auth_app_buttons)[set_index].click()
        self.wait_for_elem_to_disappear(self.rename_auth_app_buttons)
        self.get_elem(self.device_name_input).click()
        self.get_elem(self.device_name_input).send_keys(new_name)
        self.get_elem(self.confirm_button).click()
        self.wait_for_elem_to_disappear(self.device_name_input)

    def delete_auth_app(self, set_index=0):
        self.get_elems(self.delete_auth_app_buttons)[set_index].click()
        self.get_elem(self.confirm_button).click()

    def add_security_key(self, key_name):
        self.get_elem(self.add_security_key_button).click()
        self.get_elem(self.device_name_input).send_keys(key_name)
        self.get_elem(self.confirm_button).click()

    def rename_security_key(self, new_name, set_index=0):
        self.get_elems(self.rename_security_key_buttons)[set_index].click()
        self.wait_for_elem_to_disappear(self.rename_security_key_buttons)
        self.get_elem(self.device_name_input).click()
        self.get_elem(self.device_name_input).send_keys(new_name)
        self.get_elem(self.confirm_button).click()
        self.wait_for_elem_to_disappear(self.device_name_input)

    def delete_security_key(self, set_index=0):
        self.get_elems(self.delete_security_key_buttons)[set_index].click()
        self.get_elem(self.confirm_button).click()

    def enter_2fa_code(self, code):
        self.get_elem(self.check_pages_code_input).send_keys(code)
        self.get_elem(self.confirm_button).click()

    def delete_account(self, confirmation_password):
        self.get_elem(self.confirm_password_input).send_keys(confirmation_password)
        self.get_elem(self.submit_account_deletion).click()
